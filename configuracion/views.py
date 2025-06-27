from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from .models import Especie, Raza
from .forms import EspecieForm, RazaForm
from veterinaria.utils.mixins import CanDeleteMixin


# Vistas para Especies
class EspecieListView(LoginRequiredMixin, ListView):
    model = Especie
    template_name = 'configuracion/lista_especies.html'
    context_object_name = 'especies'
    ordering = ['nombre']


class EspecieCreateView(LoginRequiredMixin, CreateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'configuracion/especie_form.html'
    success_url = reverse_lazy('configuracion:lista_especies')
    
    def form_valid(self, form):
        messages.success(self.request, "Especie creada exitosamente.")
        return super().form_valid(form)


class EspecieUpdateView(LoginRequiredMixin, UpdateView):
    model = Especie
    form_class = EspecieForm
    template_name = 'configuracion/especie_form.html'
    success_url = reverse_lazy('configuracion:lista_especies')
    
    def form_valid(self, form):
        messages.success(self.request, "Especie actualizada exitosamente.")
        return super().form_valid(form)


class EspecieDeleteView(CanDeleteMixin, DeleteView):
    model = Especie
    template_name = 'configuracion/confirmar_eliminar_especie.html'
    success_url = reverse_lazy('configuracion:lista_especies')
    
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar esta especie porque tiene razas o mascotas asociadas.")
            return HttpResponseRedirect(self.success_url)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Especie eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vistas para Razas
class RazaListView(LoginRequiredMixin, ListView):
    model = Raza
    template_name = 'configuracion/lista_razas.html'
    context_object_name = 'razas'
    
    def get_queryset(self):
        queryset = Raza.objects.all().order_by('especie__nombre', 'nombre')
        # Filtrar por especie si se proporciona
        especie_id = self.request.GET.get('especie')
        if especie_id:
            queryset = queryset.filter(especie_id=especie_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['especies'] = Especie.objects.all()
        # Recuperar el filtro actual
        context['especie_seleccionada'] = self.request.GET.get('especie', '')
        return context


class RazaCreateView(LoginRequiredMixin, CreateView):
    model = Raza
    form_class = RazaForm
    template_name = 'configuracion/raza_form.html'
    success_url = reverse_lazy('configuracion:lista_razas')
    
    def form_valid(self, form):
        messages.success(self.request, "Raza creada exitosamente.")
        return super().form_valid(form)


class RazaUpdateView(LoginRequiredMixin, UpdateView):
    model = Raza
    form_class = RazaForm
    template_name = 'configuracion/raza_form.html'
    success_url = reverse_lazy('configuracion:lista_razas')
    
    def form_valid(self, form):
        messages.success(self.request, "Raza actualizada exitosamente.")
        return super().form_valid(form)


class RazaDeleteView(CanDeleteMixin, DeleteView):
    model = Raza
    template_name = 'configuracion/confirmar_eliminar_raza.html'
    success_url = reverse_lazy('configuracion:lista_razas')
    
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar esta raza porque tiene mascotas asociadas.")
            return HttpResponseRedirect(self.success_url)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Raza eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)