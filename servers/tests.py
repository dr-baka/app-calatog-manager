from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch
import requests
from .models import Server, ServerAgentMonitor
from .views import build_agent_metrics_payload, fetch_agent_metrics


class ServerAgentMonitorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='catalogadmin',
            password='strong-test-password',
        )
        self.server = Server.objects.create(name='VM 01', host_ip='10.0.0.1')
        self.monitor = ServerAgentMonitor.objects.create(
            server=self.server,
            agent_url='https://agent.example.com/metrics',
            agent_auth_key='secret-key',
        )

    @patch('servers.views.requests.get')
    def test_fetch_agent_metrics_uses_bearer_auth_header(self, mocked_get):
        mocked_response = Mock()
        mocked_response.json.return_value = {'hostname': 'vm-01'}
        mocked_response.raise_for_status.return_value = None
        mocked_get.return_value = mocked_response

        metrics = fetch_agent_metrics(self.monitor)

        self.assertEqual(metrics['hostname'], 'vm-01')
        mocked_get.assert_called_once_with(
            'https://agent.example.com/metrics',
            headers={'Authorization': 'Bearer secret-key'},
            timeout=0.8,
        )

    @patch('servers.views.fetch_agent_metrics')
    def test_build_agent_metrics_payload_marks_online_monitor(self, mocked_fetch):
        mocked_fetch.return_value = {'hostname': 'vm-01', 'cpu': {'usage_percent': 12.5}}

        payload = build_agent_metrics_payload()

        self.assertEqual(payload[0]['server_name'], 'VM 01')
        self.assertTrue(payload[0]['online'])
        self.assertEqual(payload[0]['metrics']['hostname'], 'vm-01')

    @patch('servers.views.fetch_agent_metrics')
    def test_build_agent_metrics_payload_marks_offline_monitor(self, mocked_fetch):
        mocked_fetch.side_effect = requests.RequestException('timeout')

        payload = build_agent_metrics_payload()

        self.assertFalse(payload[0]['online'])
        self.assertEqual(payload[0]['metrics'], None)
        self.assertIn('timeout', payload[0]['error'])

    def test_agent_metrics_stream_requires_login(self):
        response = self.client.get(reverse('server_agent_metrics_stream'))

        self.assertEqual(response.status_code, 302)

    @patch('servers.views.fetch_agent_metrics')
    def test_agent_monitor_panel_renders_on_dashboard(self, mocked_fetch):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live Server Agent Monitor')
        self.assertContains(response, 'VM 01')

    def test_server_create_can_add_agent_monitor(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('server_create'),
            {
                'name': 'VM 02',
                'host_ip': '10.0.0.2',
                'username': 'root',
                'os': 'Ubuntu',
                'provider': 'Local',
                'location': 'Rack 1',
                'specs': '',
                'deployment_notes': '',
                'agent_url': 'http://10.0.0.2:9000/metrics',
                'agent_auth_key': 'secret-token',
            },
        )

        self.assertRedirects(response, reverse('server_list'))
        server = Server.objects.get(name='VM 02')
        self.assertEqual(server.agent_monitor.agent_url, 'http://10.0.0.2:9000/metrics')
        self.assertEqual(server.agent_monitor.agent_auth_key, 'secret-token')

    def test_server_update_can_update_agent_monitor(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('server_update', kwargs={'pk': self.server.pk}),
            {
                'name': 'VM 01 Updated',
                'host_ip': '10.0.0.1',
                'username': '',
                'os': '',
                'provider': '',
                'location': '',
                'specs': '',
                'deployment_notes': '',
                'agent_url': 'http://10.0.0.1:9000/metrics',
                'agent_auth_key': 'new-secret',
            },
        )

        self.assertRedirects(response, reverse('server_list'))
        self.monitor.refresh_from_db()
        self.assertEqual(self.monitor.agent_url, 'http://10.0.0.1:9000/metrics')
        self.assertEqual(self.monitor.agent_auth_key, 'new-secret')
