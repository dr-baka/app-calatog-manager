from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Server

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

class ServerUpdateView(LoginRequiredMixin, UpdateView):
    model = Server
    template_name = 'catalog/server_form.html'
    fields = ['name', 'host_ip', 'username', 'os', 'provider', 'location', 'specs', 'deployment_notes']
    success_url = reverse_lazy('server_list')

class ServerDeleteView(LoginRequiredMixin, DeleteView):
    model = Server
    template_name = 'catalog/server_confirm_delete.html'
    success_url = reverse_lazy('server_list')
