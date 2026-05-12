from django.contrib import admin
from .models import Application, ApplicationEnvironment, AppAdmin, UpdateHistory

class ApplicationEnvironmentInline(admin.TabularInline):
    model = ApplicationEnvironment
    extra = 1

class AppAdminInline(admin.TabularInline):
    model = AppAdmin
    extra = 1

class UpdateHistoryInline(admin.TabularInline):
    model = UpdateHistory
    extra = 1

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'highest_environment_label')
    list_filter = ('category', 'environments__environment')
    search_fields = ('name', 'environments__url', 'environments__local_ip')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ApplicationEnvironmentInline, AppAdminInline, UpdateHistoryInline]

@admin.register(ApplicationEnvironment)
class ApplicationEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'environment', 'server', 'url', 'local_ip', 'port', 'is_active')
    list_filter = ('environment', 'is_active', 'server')
    search_fields = ('application__name', 'url', 'local_ip', 'server__name')

@admin.register(AppAdmin)
class AppAdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'application', 'role', 'email')
    search_fields = ('name', 'email', 'application__name')

@admin.register(UpdateHistory)
class UpdateHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'version', 'date')
    list_filter = ('date', 'application')
    search_fields = ('application__name', 'version', 'notes')
