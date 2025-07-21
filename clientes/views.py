from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from configuracion.models import Raza
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, Mascota
from .forms import ClienteForm, MascotaForm
from django.http import HttpResponseRedirect
from veterinaria.utils.mixins import CanDeleteMixin


# Vistas para Clientes
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista_clientes.html'
    context_object_name = 'clientes'
    ordering = ['nombre']
    

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/detalle_cliente.html'
    context_object_name = 'cliente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mascotas'] = Mascota.objects.filter(cliente=self.object)
        return context


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista_clientes')
    
    def form_valid(self, form):
        messages.success(self.request, "Cliente creado exitosamente.")
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_cliente', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado exitosamente.")
        return super().form_valid(form)


class ClienteDeleteView(CanDeleteMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/confirmar_eliminar_cliente.html'
    success_url = reverse_lazy('clientes:lista_clientes')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cliente eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vistas para Mascotas
class MascotaListView(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = 'clientes/lista_mascotas.html'
    context_object_name = 'mascotas'
    
    def get_queryset(self):
        cliente_id = self.kwargs.get('cliente_id')
        if cliente_id:
            return Mascota.objects.filter(cliente_id=cliente_id)
        return Mascota.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente_id = self.kwargs.get('cliente_id')
        if cliente_id:
            context['cliente'] = get_object_or_404(Cliente, pk=cliente_id)
        return context


class MascotaDetailView(LoginRequiredMixin, DetailView):
    model = Mascota
    template_name = 'clientes/detalle_mascota.html'
    context_object_name = 'mascota'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota = self.get_object()
        
        # Agregar información de la última cita
        context['ultima_cita'] = mascota.get_ultima_cita()
        
        return context


class MascotaCreateView(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = 'clientes/mascota_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        cliente_id = self.kwargs.get('cliente_id')
        if cliente_id:
            initial['cliente'] = cliente_id
        return initial
    
    def form_valid(self, form):
        form.instance.cliente_id = self.kwargs.get('cliente_id')
        messages.success(self.request, "Mascota creada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_cliente', kwargs={'pk': self.kwargs.get('cliente_id')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente'] = get_object_or_404(Cliente, pk=self.kwargs.get('cliente_id'))
        return context


class MascotaUpdateView(LoginRequiredMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = 'clientes/mascota_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # No necesitamos establecer el cliente inicial, 
        # ya que la instancia ya tiene un cliente asociado
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, "Mascota actualizada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cliente'] = self.object.cliente
        return context


class MascotaDeleteView(CanDeleteMixin, DeleteView):
    model = Mascota
    template_name = 'clientes/confirmar_eliminar_mascota.html'
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_cliente', kwargs={'pk': self.object.cliente.pk})
    
    def delete(self, request, *args, **kwargs):
        mascota = self.get_object()
        cliente_id = mascota.cliente.id
        messages.success(request, "Mascota eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)

@login_required 
def get_razas_by_especie(request):
    especie_id = request.GET.get('especie_id')
    razas = Raza.objects.filter(especie_id=especie_id).values('id', 'nombre')
    return JsonResponse(list(razas), safe=False)

#--------------------------------------------------------------------------------------------------------------------------------
