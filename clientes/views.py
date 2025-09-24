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
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q


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
class MascotasCumpleanosView(LoginRequiredMixin, ListView):
    model = Mascota
    template_name = 'clientes/cumpleanos_mascotas.html'
    context_object_name = 'mascotas'
    
    def get_queryset(self):
        periodo = self.request.GET.get('periodo', 'hoy')
        
        # Solo mascotas con fecha de nacimiento y activas
        queryset = Mascota.objects.filter(
            fecha_nacimiento__isnull=False,
            activa=True
        ).select_related('cliente', 'especie', 'raza').order_by('nombre')
        
        today = date.today()
        
        if periodo == 'hoy':
            # Mascotas que cumplen años hoy
            queryset = queryset.filter(
                fecha_nacimiento__month=today.month,
                fecha_nacimiento__day=today.day
            )
        elif periodo == 'semana':
            # Próximos 7 días
            end_date = today + timedelta(days=7)
            
            # Si no cruza el año
            if today.year == end_date.year:
                queryset = queryset.filter(
                    Q(fecha_nacimiento__month=today.month, 
                      fecha_nacimiento__day__gte=today.day) |
                    Q(fecha_nacimiento__month=end_date.month,
                      fecha_nacimiento__day__lte=end_date.day,
                      fecha_nacimiento__month__gt=today.month)
                )
            else:
                # Cruza el año (ej: diciembre a enero)
                queryset = queryset.filter(
                    Q(fecha_nacimiento__month=today.month,
                      fecha_nacimiento__day__gte=today.day) |
                    Q(fecha_nacimiento__month=end_date.month,
                      fecha_nacimiento__day__lte=end_date.day)
                )
        elif periodo == 'mes':
            # Todo el mes actual
            queryset = queryset.filter(
                fecha_nacimiento__month=today.month
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.request.GET.get('periodo', 'hoy')
        today = date.today()
        
        context['periodo_actual'] = periodo
        context['fecha_hoy'] = today
        
        # Calcular información adicional para cada mascota
        mascotas_con_info = []
        for mascota in context['mascotas']:
            # Calcular próximo cumpleaños
            cumple_este_ano = date(today.year, mascota.fecha_nacimiento.month, mascota.fecha_nacimiento.day)
            
            if cumple_este_ano < today:
                proximo_cumple = date(today.year + 1, mascota.fecha_nacimiento.month, mascota.fecha_nacimiento.day)
            else:
                proximo_cumple = cumple_este_ano
            
            # Días hasta el cumpleaños
            dias_hasta = (proximo_cumple - today).days
            
            # Edad que cumplirá
            edad_cumplira = proximo_cumple.year - mascota.fecha_nacimiento.year
            
            # Es hoy?
            es_hoy = dias_hasta == 0
            
            mascotas_con_info.append({
                'mascota': mascota,
                'proximo_cumple': proximo_cumple,
                'dias_hasta': dias_hasta,
                'edad_cumplira': edad_cumplira,
                'es_hoy': es_hoy,
                'edad_actual': mascota.edad() or 0
            })
        
        # Ordenar por días hasta cumpleaños
        mascotas_con_info.sort(key=lambda x: x['dias_hasta'])
        
        context['mascotas_info'] = mascotas_con_info
        context['total_mascotas'] = len(mascotas_con_info)
        
        # Estadísticas
        hoy = sum(1 for m in mascotas_con_info if m['es_hoy'])
        context['estadisticas'] = {
            'hoy': hoy,
            'esta_semana': len([m for m in mascotas_con_info if m['dias_hasta'] <= 7]),
            'este_mes': len(mascotas_con_info)
        }
        
        return context

@login_required 
def get_razas_by_especie(request):
    especie_id = request.GET.get('especie_id')
    razas = Raza.objects.filter(especie_id=especie_id).values('id', 'nombre')
    return JsonResponse(list(razas), safe=False)

#--------------------------------------------------------------------------------------------------------------------------------
