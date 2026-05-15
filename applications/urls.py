from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApplicationListView.as_view(), name='application_list'),
    path('create/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('status/stream/', views.application_status_stream, name='application_status_stream'),
    path('<int:pk>/status/', views.application_status, name='application_status'),
    path('environments/<int:pk>/status/', views.application_environment_status, name='application_environment_status'),
    path('<slug:slug>/environments/create/', views.ApplicationEnvironmentCreateView.as_view(), name='application_environment_create'),
    path('environments/<int:pk>/update/', views.ApplicationEnvironmentUpdateView.as_view(), name='application_environment_update'),
    path('environments/<int:pk>/delete/', views.ApplicationEnvironmentDeleteView.as_view(), name='application_environment_delete'),
    path('<slug:slug>/admins/create/', views.AppAdminCreateView.as_view(), name='app_admin_create'),
    path('admins/<int:pk>/update/', views.AppAdminUpdateView.as_view(), name='app_admin_update'),
    path('admins/<int:pk>/delete/', views.AppAdminDeleteView.as_view(), name='app_admin_delete'),
    path('<slug:slug>/history/create/', views.UpdateHistoryCreateView.as_view(), name='update_history_create'),
    path('history/<int:pk>/update/', views.UpdateHistoryUpdateView.as_view(), name='update_history_update'),
    path('history/<int:pk>/delete/', views.UpdateHistoryDeleteView.as_view(), name='update_history_delete'),
    path('<slug:slug>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('<slug:slug>/update/', views.ApplicationUpdateView.as_view(), name='application_update'),
    path('<slug:slug>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
]
