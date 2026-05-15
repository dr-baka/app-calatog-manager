from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch
import requests
from .models import AppAdmin, Application, ApplicationEnvironment, UpdateHistory
from .views import build_application_status_payload, build_status_endpoints
from categories.models import Category
from servers.models import Server


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='catalogadmin',
            password='strong-test-password',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'App Catalog Manager')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_login_page_supports_english_language(self):
        response = self.client.get(reverse('login'), HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage applications, servers, and categories from one place.')
        self.assertContains(response, 'Sign in')

    def test_language_toggle_stores_selected_language(self):
        response = self.client.post('/i18n/setlang/', {'language': 'en', 'next': reverse('login')})

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(self.client.cookies['django_language'].value, 'en')

    def test_logout_ends_authenticated_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class ApplicationManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='catalogadmin',
            password='strong-test-password',
        )
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Platform')
        self.server = Server.objects.create(name='Main Server', host_ip='10.10.10.5')
        self.app = Application.objects.create(
            name='Data Portal',
            category=self.category,
            description='**Portal** internal',
            maintenance_notes='- restart worker',
            deployment_notes='`deploy.sh`',
        )

    def test_application_detail_renders_markdown_fields(self):
        UpdateHistory.objects.create(
            application=self.app,
            version='v1.2.0',
            notes='**Fix** cache',
        )
        AppAdmin.objects.create(
            application=self.app,
            name='Admin One',
            email='admin@example.com',
            access_notes='Use `vpn` first',
        )

        response = self.client.get(reverse('application_detail', kwargs={'slug': self.app.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<strong>Portal</strong>', html=True)
        self.assertContains(response, '<code>deploy.sh</code>', html=True)
        self.assertContains(response, '<strong>Fix</strong>', html=True)
        self.assertContains(response, '<code>vpn</code>', html=True)

    def test_can_create_application_admin_from_application_detail(self):
        response = self.client.post(
            reverse('app_admin_create', kwargs={'slug': self.app.slug}),
            {
                'name': 'Ops Lead',
                'username': 'opslead',
                'email': 'ops@example.com',
                'role': 'Owner',
                'whatsapp': '6281234567890',
                'access_notes': '**Primary** contact',
            },
        )

        self.assertRedirects(response, reverse('application_detail', kwargs={'slug': self.app.slug}))
        self.assertTrue(self.app.admins.filter(email='ops@example.com').exists())

    def test_can_create_update_history_from_application_detail(self):
        response = self.client.post(
            reverse('update_history_create', kwargs={'slug': self.app.slug}),
            {
                'version': 'v2.0.0',
                'notes': '- release API',
            },
        )

        self.assertRedirects(response, reverse('application_detail', kwargs={'slug': self.app.slug}))
        self.assertTrue(self.app.history.filter(version='v2.0.0').exists())

    def test_status_endpoint_uses_app_url_then_https_local_then_http_local(self):
        environment = ApplicationEnvironment.objects.create(
            application=self.app,
            environment='PROD',
            server=self.server,
            url='https://portal.example.com',
            local_ip='10.10.10.5',
            port='8080',
        )

        endpoints = build_status_endpoints(environment)

        self.assertEqual(endpoints, [
            'https://portal.example.com',
            'https://10.10.10.5:8080',
            'http://10.10.10.5:8080',
        ])

    @patch('applications.views.requests.get')
    def test_status_endpoint_falls_back_until_endpoint_is_online(self, mocked_get):
        ApplicationEnvironment.objects.create(
            application=self.app,
            environment='PROD',
            server=self.server,
            url='https://portal.example.com',
            local_ip='10.10.10.5',
            port='8080',
        )
        mocked_get.side_effect = [
            requests.RequestException('app url down'),
            requests.RequestException('https local down'),
            Mock(status_code=200),
        ]

        response = self.client.get(reverse('application_status', kwargs={'pk': self.app.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'online')
        self.assertEqual(response.json()['checked_url'], 'http://10.10.10.5:8080')
        self.assertEqual(mocked_get.call_count, 3)

    def test_application_status_stream_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse('application_status_stream'))

        self.assertEqual(response.status_code, 302)

    @patch('applications.views.is_endpoint_online')
    def test_application_status_payload_uses_highest_environment(self, mocked_online):
        ApplicationEnvironment.objects.create(
            application=self.app,
            environment='DEV',
            server=self.server,
            url='https://dev.example.com',
        )
        ApplicationEnvironment.objects.create(
            application=self.app,
            environment='PROD',
            server=self.server,
            url='https://prod.example.com',
        )
        mocked_online.return_value = True

        payload = build_application_status_payload()
        app_payload = next(item for item in payload if item['app_id'] == self.app.pk)

        self.assertTrue(app_payload['online'])
        self.assertEqual(app_payload['environment'], 'PROD')
        self.assertEqual(app_payload['checked_url'], 'https://prod.example.com')

    def test_highest_environment_uses_dev_beta_prod_order(self):
        ApplicationEnvironment.objects.create(application=self.app, environment='DEV', server=self.server)
        self.assertEqual(self.app.highest_environment_label, 'DEV')

        ApplicationEnvironment.objects.create(application=self.app, environment='BETA', server=self.server)
        self.assertEqual(self.app.highest_environment_label, 'BETA')

        ApplicationEnvironment.objects.create(application=self.app, environment='PROD', server=self.server)
        self.assertEqual(self.app.highest_environment_label, 'PROD')

    def test_application_can_only_have_one_record_per_environment(self):
        ApplicationEnvironment.objects.create(application=self.app, environment='PROD', server=self.server)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApplicationEnvironment.objects.create(application=self.app, environment='PROD', server=self.server)

    def test_application_detail_shows_all_environments_in_order(self):
        ApplicationEnvironment.objects.create(application=self.app, environment='PROD', server=self.server)
        ApplicationEnvironment.objects.create(application=self.app, environment='DEV', server=self.server)
        ApplicationEnvironment.objects.create(application=self.app, environment='BETA', server=self.server)

        response = self.client.get(reverse('application_detail', kwargs={'slug': self.app.slug}))
        content = response.content.decode()
        environments_section = content[content.index('Environment Server'):]

        self.assertLess(environments_section.index('>DEV<'), environments_section.index('>BETA<'))
        self.assertLess(environments_section.index('>BETA<'), environments_section.index('>PROD<'))

    def test_can_create_application_environment_from_application_detail(self):
        response = self.client.post(
            reverse('application_environment_create', kwargs={'slug': self.app.slug}),
            {
                'environment': 'DEV',
                'server': self.server.pk,
                'url': 'https://dev.example.com',
                'local_ip': '10.10.10.6',
                'port': '8000',
                'is_active': 'on',
                'deployment_notes': '**Deploy** dev',
            },
        )

        self.assertRedirects(response, reverse('application_detail', kwargs={'slug': self.app.slug}))
        self.assertTrue(self.app.environments.filter(environment='DEV', url='https://dev.example.com').exists())

    def test_core_catalog_pages_support_english_language(self):
        ApplicationEnvironment.objects.create(application=self.app, environment='PROD', server=self.server)

        pages = [
            (reverse('dashboard'), 'Application List'),
            (reverse('application_list'), 'All Applications'),
            (reverse('application_detail', kwargs={'slug': self.app.slug}), 'Application Details'),
            (reverse('category_list'), 'Application Categories'),
            (reverse('server_list'), 'Server Management'),
        ]

        for url, expected_text in pages:
            with self.subTest(url=url):
                response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)
