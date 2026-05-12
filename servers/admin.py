from django.contrib import admin
from .models import Server

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_ip', 'provider', 'location')
    search_fields = ('name', 'host_ip')
