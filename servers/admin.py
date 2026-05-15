from django.contrib import admin
from .models import Server, ServerAgentMonitor


class ServerAgentMonitorInline(admin.StackedInline):
    model = ServerAgentMonitor
    extra = 0

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_ip', 'provider', 'location')
    search_fields = ('name', 'host_ip')
    inlines = [ServerAgentMonitorInline]


@admin.register(ServerAgentMonitor)
class ServerAgentMonitorAdmin(admin.ModelAdmin):
    list_display = ('server', 'agent_url')
    search_fields = ('server__name', 'server__host_ip', 'agent_url')
