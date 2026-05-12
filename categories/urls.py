from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('<slug:slug>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
