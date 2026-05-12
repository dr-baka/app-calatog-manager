from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Count
from django.db.models import Prefetch
from urllib.parse import urlparse
import requests
import urllib3
from .models import Application, ApplicationEnvironment, AppAdmin, UpdateHistory
from categories.models import Category
from servers.models import Server

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@login_required
def dashboard(request):
    apps = Application.objects.all().select_related('category').prefetch_related(
        Prefetch('environments', queryset=ApplicationEnvironment.objects.select_related('server'))
    )
    categories_count = Category.objects.count()
    servers_count = Server.objects.count()
    
    # Environment stats
    env_stats = ApplicationEnvironment.objects.values('environment').annotate(count=Count('application', distinct=True))
    env_map = {item['environment']: item['count'] for item in env_stats}
    
    context = {
        'apps': apps,
        'total_apps': apps.count(),
        'total_categories': categories_count,
        'total_servers': servers_count,
        'dev_count': env_map.get('DEV', 0),
        'beta_count': env_map.get('BETA', 0),
        'prod_count': env_map.get('PROD', 0),
    }
    return render(request, 'catalog/dashboard.html', context)


@login_required
def application_status(request, pk):
    application = Application.objects.get(pk=pk)
    environment = application.highest_environment

    if not environment:
        return JsonResponse({
            'online': False,
            'status': 'offline',
            'checked_url': None,
            'checked_urls': [],
        })

    return environment_status_response(environment)


@login_required
def application_environment_status(request, pk):
    environment = get_object_or_404(ApplicationEnvironment, pk=pk)
    return environment_status_response(environment)


def environment_status_response(environment):
    endpoints = build_status_endpoints(environment)
    for endpoint in endpoints:
        if is_endpoint_online(endpoint):
            return JsonResponse({
                'online': True,
                'status': 'online',
                'checked_url': endpoint,
            })

    return JsonResponse({
        'online': False,
        'status': 'offline',
        'checked_url': None,
        'checked_urls': endpoints,
    })


def build_status_endpoints(environment):
    endpoints = []

    if environment.url:
        endpoints.append(environment.url)

    if environment.local_ip and environment.port:
        host = _normalize_host(environment.local_ip)
        endpoints.extend([
            f'https://{host}:{environment.port}',
            f'http://{host}:{environment.port}',
        ])

    return list(dict.fromkeys(endpoints))


def is_endpoint_online(endpoint):
    try:
        response = requests.get(
            endpoint,
            timeout=3,
            allow_redirects=True,
            verify=False,
            headers={'User-Agent': 'AppCatalogStatusCheck/1.0'},
        )
        return response.status_code < 500
    except requests.RequestException:
        return False


def _normalize_host(value):
    parsed = urlparse(value if '://' in value else f'//{value}')
    return parsed.netloc or parsed.path

class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'catalog/application_list.html'
    context_object_name = 'apps'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related(
            Prefetch('environments', queryset=ApplicationEnvironment.objects.select_related('server'))
        )
        category_slug = self.request.GET.get('category')
        env = self.request.GET.get('env')
        search = self.request.GET.get('q')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if env:
            queryset = queryset.filter(environments__environment=env)
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset.distinct()

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'catalog/application_detail.html'
    context_object_name = 'app'

    def get_queryset(self):
        return super().get_queryset().select_related('category').prefetch_related(
            Prefetch('environments', queryset=ApplicationEnvironment.objects.select_related('server'))
        )

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    template_name = 'catalog/application_form.html'
    fields = [
        'name', 'description', 'category', 'logo_url', 'logo_image',
        'framework', 'database',
        'repository', 'maintenance_notes', 'deployment_notes'
    ]
    success_url = reverse_lazy('dashboard')

class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    template_name = 'catalog/application_form.html'
    fields = [
        'name', 'description', 'category', 'logo_url', 'logo_image',
        'framework', 'database',
        'repository', 'maintenance_notes', 'deployment_notes'
    ]
    success_url = reverse_lazy('dashboard')

class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'catalog/application_confirm_delete.html'
    success_url = reverse_lazy('dashboard')


class ApplicationEnvironmentCreateView(LoginRequiredMixin, CreateView):
    model = ApplicationEnvironment
    template_name = 'catalog/generic_form.html'
    fields = ['environment', 'server', 'url', 'local_ip', 'port', 'is_active', 'deployment_notes']

    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(Application, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.application = self.application
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.application.slug})


class ApplicationEnvironmentUpdateView(LoginRequiredMixin, UpdateView):
    model = ApplicationEnvironment
    template_name = 'catalog/generic_form.html'
    fields = ['environment', 'server', 'url', 'local_ip', 'port', 'is_active', 'deployment_notes']

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})


class ApplicationEnvironmentDeleteView(LoginRequiredMixin, DeleteView):
    model = ApplicationEnvironment
    template_name = 'catalog/application_environment_confirm_delete.html'

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})


class AppAdminCreateView(LoginRequiredMixin, CreateView):
    model = AppAdmin
    template_name = 'catalog/generic_form.html'
    fields = ['name', 'username', 'email', 'role', 'whatsapp', 'access_notes']

    def dispatch(self, request, *args, **kwargs):
        self.application = Application.objects.get(slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.application = self.application
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.application.slug})


class AppAdminUpdateView(LoginRequiredMixin, UpdateView):
    model = AppAdmin
    template_name = 'catalog/generic_form.html'
    fields = ['name', 'username', 'email', 'role', 'whatsapp', 'access_notes']

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})


class AppAdminDeleteView(LoginRequiredMixin, DeleteView):
    model = AppAdmin
    template_name = 'catalog/app_admin_confirm_delete.html'

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})


class UpdateHistoryCreateView(LoginRequiredMixin, CreateView):
    model = UpdateHistory
    template_name = 'catalog/generic_form.html'
    fields = ['version', 'notes']

    def dispatch(self, request, *args, **kwargs):
        self.application = Application.objects.get(slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.application = self.application
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.application.slug})


class UpdateHistoryUpdateView(LoginRequiredMixin, UpdateView):
    model = UpdateHistory
    template_name = 'catalog/generic_form.html'
    fields = ['version', 'notes']

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})


class UpdateHistoryDeleteView(LoginRequiredMixin, DeleteView):
    model = UpdateHistory
    template_name = 'catalog/update_history_confirm_delete.html'

    def get_success_url(self):
        return reverse('application_detail', kwargs={'slug': self.object.application.slug})
