from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Category

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'catalog/category_form.html'
    fields = ['name', 'description', 'color', 'icon']
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'catalog/category_form.html'
    fields = ['name', 'description', 'color', 'icon']
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'catalog/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
