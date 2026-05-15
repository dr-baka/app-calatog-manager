from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json
import time
import requests
from .models import Server, ServerAgentMonitor


def fetch_agent_metrics(monitor):
    response = requests.get(
        monitor.agent_url,
        headers={'Authorization': f'Bearer {monitor.agent_auth_key}'},
        timeout=0.8,
    )
    response.raise_for_status()
    return response.json()


def build_agent_metrics_payload():
    payload = []
    monitors = ServerAgentMonitor.objects.select_related('server').order_by('server__name')

    for monitor in monitors:
        item = {
            'server_id': monitor.server_id,
            'server_name': monitor.server.name,
            'host_ip': monitor.server.host_ip,
            'agent_url': monitor.agent_url,
            'online': False,
            'error': None,
            'metrics': None,
        }
        try:
            item['metrics'] = fetch_agent_metrics(monitor)
            item['online'] = True
        except requests.RequestException as exc:
            item['error'] = str(exc)
        except ValueError as exc:
            item['error'] = f'Invalid JSON: {exc}'

        payload.append(item)

    return payload


@login_required
def server_agent_metrics_stream(request):
    def event_stream():
        while True:
            payload = build_agent_metrics_payload()
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

class ServerListView(LoginRequiredMixin, ListView):
    model = Server
    template_name = 'catalog/server_list.html'
    context_object_name = 'servers'

    def get_queryset(self):
        return super().get_queryset().annotate(applications_count=Count('application_environments__application', distinct=True))

class ServerCreateView(LoginRequiredMixin, CreateView):
    model = Server
    template_name = 'catalog/server_form.html'
    fields = ['name', 'host_ip', 'username', 'os', 'provider', 'location', 'specs', 'deployment_notes']
    success_url = reverse_lazy('server_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_agent_monitor_modal'] = True
        context['agent_monitor'] = None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        save_agent_monitor(self.object, self.request.POST)
        return response

class ServerUpdateView(LoginRequiredMixin, UpdateView):
    model = Server
    template_name = 'catalog/server_form.html'
    fields = ['name', 'host_ip', 'username', 'os', 'provider', 'location', 'specs', 'deployment_notes']
    success_url = reverse_lazy('server_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_agent_monitor_modal'] = True
        try:
            context['agent_monitor'] = self.object.agent_monitor
        except ServerAgentMonitor.DoesNotExist:
            context['agent_monitor'] = None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        save_agent_monitor(self.object, self.request.POST)
        return response

class ServerDeleteView(LoginRequiredMixin, DeleteView):
    model = Server
    template_name = 'catalog/server_confirm_delete.html'
    success_url = reverse_lazy('server_list')


def save_agent_monitor(server, data):
    agent_url = data.get('agent_url', '').strip()
    agent_auth_key = data.get('agent_auth_key', '').strip()

    if not agent_url and not agent_auth_key:
        return

    ServerAgentMonitor.objects.update_or_create(
        server=server,
        defaults={
            'agent_url': agent_url,
            'agent_auth_key': agent_auth_key,
        },
    )
