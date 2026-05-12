from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from applications.views import dashboard

urlpatterns = [
    path(settings.ADMIN_PATH, admin.site.urls),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
    path('apps/', include('applications.urls')),
    path('categories/', include('categories.urls')),
    path('servers/', include('servers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
