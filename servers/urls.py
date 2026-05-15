from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServerListView.as_view(), name='server_list'),
    path('agents/metrics/stream/', views.server_agent_metrics_stream, name='server_agent_metrics_stream'),
    path('create/', views.ServerCreateView.as_view(), name='server_create'),
    path('<int:pk>/update/', views.ServerUpdateView.as_view(), name='server_update'),
    path('<int:pk>/delete/', views.ServerDeleteView.as_view(), name='server_delete'),
]
