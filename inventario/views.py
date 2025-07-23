from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from clientes.models import Mascota
from .models import Vacuna, VacunaAplicada, Producto, ProductoAplicado
from .forms import VacunaForm, VacunaAplicadaForm, ProductoForm, ProductoAplicadoForm,VacunaAgendadaForm, AplicarVacunaAgendadaForm, ProductoAgendadoForm, AplicarProductoAgendadoForm
from veterinaria.utils.mixins import CanDeleteMixin


# Vistas para Vacunas
class VacunaListView(LoginRequiredMixin, ListView):
    model = Vacuna
    template_name = 'inventario/lista_vacunas.html'
    context_object_name = 'vacunas'
    ordering = ['nombre']


class VacunaDetailView(LoginRequiredMixin, DetailView):
    model = Vacuna
    template_name = 'inventario/detalle_vacuna.html'
    context_object_name = 'vacuna'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Listar todas las aplicaciones de esta vacuna
        context['aplicaciones'] = VacunaAplicada.objects.filter(vacuna=self.object).order_by('-fecha_aplicacion')
        return context


class VacunaCreateView(LoginRequiredMixin, CreateView):
    model = Vacuna
    form_class = VacunaForm
    template_name = 'inventario/vacuna_form.html'
    success_url = reverse_lazy('inventario:lista_vacunas')
    
    def form_valid(self, form):
        messages.success(self.request, "Vacuna creada exitosamente.")
        return super().form_valid(form)


class VacunaUpdateView(LoginRequiredMixin, UpdateView):
    model = Vacuna
    form_class = VacunaForm
    template_name = 'inventario/vacuna_form.html'
    
    def get_success_url(self):
        return reverse_lazy('inventario:detalle_vacuna', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Vacuna actualizada exitosamente.")
        return super().form_valid(form)


class VacunaDeleteView(CanDeleteMixin, DeleteView):
    model = Vacuna
    template_name = 'inventario/confirmar_eliminar_vacuna.html'
    success_url = reverse_lazy('inventario:lista_vacunas')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Vacuna eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vistas para Vacunas Aplicadas
class VacunaAplicadaCreateView(LoginRequiredMixin, CreateView):
    model = VacunaAplicada
    form_class = VacunaAplicadaForm
    template_name = 'inventario/vacuna_aplicada_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Corregir: pasar la mascota en initial, no como mascota_id
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        kwargs['initial'] = {'mascota': mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        # Verificar si viene desde una consulta
        context['from_consulta'] = self.request.GET.get('from_consulta', False)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        form.instance.mascota = mascota
        
        try:
            messages.success(self.request, f"Vacuna aplicada exitosamente a {mascota.nombre}.")
            return super().form_valid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        # Si viene desde consulta, redirigir de vuelta al perfil de la mascota
        if self.request.GET.get('from_consulta'):
            messages.info(self.request, "Puedes continuar con la consulta desde el perfil de la mascota.")
            return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})


class VacunaAplicadaDetailView(LoginRequiredMixin, DetailView):
    model = VacunaAplicada
    template_name = 'inventario/detalle_vacuna_aplicada.html'
    context_object_name = 'vacuna_aplicada'


class VacunaAplicadaUpdateView(LoginRequiredMixin, UpdateView):
    model = VacunaAplicada
    form_class = VacunaAplicadaForm
    template_name = 'inventario/vacuna_aplicada_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Corregir: pasar la mascota en initial
        kwargs['initial'] = {'mascota': self.object.mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mascota'] = self.object.mascota
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Registro de vacuna actualizado exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.object.mascota.id})


class VacunaAplicadaDeleteView(CanDeleteMixin, DeleteView):
    model = VacunaAplicada
    template_name = 'inventario/confirmar_eliminar_vacuna_aplicada.html'
    context_object_name = 'vacuna_aplicada'  # Agregar esto para asegurar el contexto
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Debug: verificar que la mascota existe y tiene ID
        vacuna_aplicada = self.get_object()
        print(f"Debug - Vacuna aplicada ID: {vacuna_aplicada.id}")
        print(f"Debug - Mascota: {vacuna_aplicada.mascota}")
        print(f"Debug - Mascota ID: {vacuna_aplicada.mascota.id if vacuna_aplicada.mascota else 'None'}")
        
        # Asegurar que tenemos el objeto correcto en el contexto
        context['vacuna_aplicada'] = vacuna_aplicada
        return context
    
    def get_success_url(self):
        # Obtener el objeto antes de eliminarlo
        vacuna_aplicada = self.get_object()
        mascota_id = vacuna_aplicada.mascota.id
        
        # Verificar que tenemos un ID válido
        if not mascota_id:
            # Si no hay ID, redirigir a la lista de mascotas como fallback
            return reverse_lazy('clientes:lista_mascotas')
        
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': mascota_id})
    
    def delete(self, request, *args, **kwargs):
        # Obtener información antes de eliminar
        vacuna_aplicada = self.get_object()
        mascota_nombre = vacuna_aplicada.mascota.nombre if vacuna_aplicada.mascota else "mascota desconocida"
        
        messages.success(
            self.request, 
            f"Registro de vacuna eliminado exitosamente para {mascota_nombre}."
        )
        return super().delete(request, *args, **kwargs)


# Vistas para Productos (Antiparasitarios/Vermífugos)
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'inventario/lista_productos.html'
    context_object_name = 'productos'
    ordering = ['nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por tipo si se proporciona
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = 'inventario/detalle_producto.html'
    context_object_name = 'producto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Listar todas las aplicaciones de este producto
        context['aplicaciones'] = ProductoAplicado.objects.filter(producto=self.object).order_by('-fecha_aplicacion')
        return context


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    success_url = reverse_lazy('inventario:lista_productos')
    
    def form_valid(self, form):
        messages.success(self.request, "Producto creado exitosamente.")
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/producto_form.html'
    
    def get_success_url(self):
        return reverse_lazy('inventario:detalle_producto', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado exitosamente.")
        return super().form_valid(form)


class ProductoDeleteView(CanDeleteMixin, DeleteView):
    model = Producto
    template_name = 'inventario/confirmar_eliminar_producto.html'
    success_url = reverse_lazy('inventario:lista_productos')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Producto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vistas para Productos Aplicados
class ProductoAplicadoCreateView(LoginRequiredMixin, CreateView):
    model = ProductoAplicado
    form_class = ProductoAplicadoForm
    template_name = 'inventario/producto_aplicado_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Corregir: pasar la mascota en initial, no como mascota_id
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        kwargs['initial'] = {'mascota': mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        # Verificar si viene desde una consulta
        context['from_consulta'] = self.request.GET.get('from_consulta', False)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        form.instance.mascota = mascota
        
        try:
            messages.success(self.request, f"Producto aplicado exitosamente a {mascota.nombre}.")
            return super().form_valid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        # Si viene desde consulta, redirigir de vuelta al perfil de la mascota
        if self.request.GET.get('from_consulta'):
            messages.info(self.request, "Puedes continuar con la consulta desde el perfil de la mascota.")
            return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})


class ProductoAplicadoDetailView(LoginRequiredMixin, DetailView):
    model = ProductoAplicado
    template_name = 'inventario/detalle_producto_aplicado.html'
    context_object_name = 'producto_aplicado'


class ProductoAplicadoUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductoAplicado
    form_class = ProductoAplicadoForm
    template_name = 'inventario/producto_aplicado_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Corregir: pasar la mascota en initial
        kwargs['initial'] = {'mascota': self.object.mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mascota'] = self.object.mascota
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Registro de producto actualizado exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.object.mascota.id})


class ProductoAplicadoDeleteView(CanDeleteMixin, DeleteView):
    model = ProductoAplicado
    template_name = 'inventario/confirmar_eliminar_producto_aplicado.html'
    
    def get_success_url(self):
        mascota_id = self.object.mascota.id
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': mascota_id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Registro de producto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)
    
# ============================================================================
# NUEVAS VISTAS PARA SISTEMA DE AGENDAMIENTO
# ============================================================================

from .forms import (
    VacunaAgendadaForm, AplicarVacunaAgendadaForm,
    ProductoAgendadoForm, AplicarProductoAgendadoForm
)

# === VISTAS PARA AGENDAR VACUNAS ===

class VacunaAgendadaCreateView(LoginRequiredMixin, CreateView):
    """Vista para AGENDAR una vacuna (sin aplicar)"""
    model = VacunaAplicada
    form_class = VacunaAgendadaForm
    template_name = 'inventario/agendar_vacuna.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        kwargs['initial'] = {'mascota': mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        context['from_consulta'] = self.request.GET.get('from_consulta', False)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        form.instance.mascota = mascota
        
        try:
            messages.success(self.request, f"Vacuna agendada exitosamente para {mascota.nombre}.")
            return super().form_valid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        if self.request.GET.get('from_consulta'):
            messages.info(self.request, "Puedes continuar con la consulta desde el perfil de la mascota.")
            return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})


class AplicarVacunaAgendadaView(LoginRequiredMixin, UpdateView):
    """Vista para APLICAR una vacuna que estaba agendada"""
    model = VacunaAplicada
    form_class = AplicarVacunaAgendadaForm
    template_name = 'inventario/aplicar_vacuna_agendada.html'
    
    def get_queryset(self):
        # Solo vacunas agendadas (sin fecha_aplicacion)
        return VacunaAplicada.objects.filter(fecha_aplicacion__isnull=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacuna_agendada'] = self.object
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Vacuna aplicada exitosamente a {self.object.mascota.nombre}.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.object.mascota.id})


class VacunasAgendadasListView(LoginRequiredMixin, ListView):
    """Lista de todas las vacunas agendadas (pendientes de aplicar)"""
    model = VacunaAplicada
    template_name = 'inventario/vacunas_agendadas.html'
    context_object_name = 'vacunas_agendadas'
    
    def get_queryset(self):
        queryset = VacunaAplicada.objects.filter(
            fecha_aplicacion__isnull=True
        ).select_related('mascota', 'vacuna').order_by('fecha_proxima')
        
        # Filtrar por mascota si se proporciona
        mascota_id = self.request.GET.get('mascota')
        if mascota_id:
            queryset = queryset.filter(mascota_id=mascota_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar información de días restantes
        hoy = timezone.now().date()
        for vacuna in context['vacunas_agendadas']:
            if vacuna.fecha_proxima:
                delta = vacuna.fecha_proxima - hoy
                vacuna.dias_restantes = delta.days
            else:
                vacuna.dias_restantes = None
        
        # Agregar filtros disponibles
        context['mascotas'] = Mascota.objects.filter(
            activa=True,
            vacunas_aplicadas__fecha_aplicacion__isnull=True
        ).distinct().order_by('nombre')
        
        return context


# === VISTAS PARA AGENDAR PRODUCTOS ===

class ProductoAgendadoCreateView(LoginRequiredMixin, CreateView):
    """Vista para AGENDAR un producto (sin aplicar)"""
    model = ProductoAplicado
    form_class = ProductoAgendadoForm
    template_name = 'inventario/agendar_producto.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        kwargs['initial'] = {'mascota': mascota}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        context['from_consulta'] = self.request.GET.get('from_consulta', False)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        form.instance.mascota = mascota
        
        try:
            messages.success(self.request, f"Producto agendado exitosamente para {mascota.nombre}.")
            return super().form_valid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_success_url(self):
        if self.request.GET.get('from_consulta'):
            messages.info(self.request, "Puedes continuar con la consulta desde el perfil de la mascota.")
            return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.kwargs.get('mascota_id')})


class AplicarProductoAgendadoView(LoginRequiredMixin, UpdateView):
    """Vista para APLICAR un producto que estaba agendado"""
    model = ProductoAplicado
    form_class = AplicarProductoAgendadoForm
    template_name = 'inventario/aplicar_producto_agendado.html'
    
    def get_queryset(self):
        # Solo productos agendados (sin fecha_aplicacion)
        return ProductoAplicado.objects.filter(fecha_aplicacion__isnull=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto_agendado'] = self.object
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Producto aplicado exitosamente a {self.object.mascota.nombre}.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('clientes:detalle_mascota', kwargs={'pk': self.object.mascota.id})


class ProductosAgendadosListView(LoginRequiredMixin, ListView):
    """Lista de todos los productos agendados (pendientes de aplicar)"""
    model = ProductoAplicado
    template_name = 'inventario/productos_agendados.html'
    context_object_name = 'productos_agendados'
    
    def get_queryset(self):
        queryset = ProductoAplicado.objects.filter(
            fecha_aplicacion__isnull=True
        ).select_related('mascota', 'producto').order_by('fecha_proxima')
        
        # Filtrar por mascota si se proporciona
        mascota_id = self.request.GET.get('mascota')
        if mascota_id:
            queryset = queryset.filter(mascota_id=mascota_id)
        
        # Filtrar por tipo de producto si se proporciona
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(producto__tipo=tipo)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar información de días restantes
        hoy = timezone.now().date()
        for producto in context['productos_agendados']:
            if producto.fecha_proxima:
                delta = producto.fecha_proxima - hoy
                producto.dias_restantes = delta.days
            else:
                producto.dias_restantes = None
        
        # Agregar filtros disponibles
        context['mascotas'] = Mascota.objects.filter(
            activa=True,
            productos_aplicados__fecha_aplicacion__isnull=True
        ).distinct().order_by('nombre')
        
        context['tipos_producto'] = Producto.TIPO_CHOICES
        
        return context


# === VISTA COMBINADA PARA AGENDA GENERAL ===

class AgendaGeneralView(LoginRequiredMixin, View):
    """Vista que muestra tanto vacunas como productos agendados"""
    template_name = 'inventario/agenda_general.html'
    
    def get(self, request, *args, **kwargs):
        hoy = timezone.now().date()
        fecha_limite = hoy + timedelta(days=30)
        
        # Vacunas agendadas próximas
        vacunas_agendadas = VacunaAplicada.objects.filter(
            fecha_aplicacion__isnull=True,
            fecha_proxima__lte=fecha_limite
        ).select_related('mascota', 'vacuna').order_by('fecha_proxima')
        
        # Productos agendados próximos
        productos_agendados = ProductoAplicado.objects.filter(
            fecha_aplicacion__isnull=True,
            fecha_proxima__lte=fecha_limite
        ).select_related('mascota', 'producto').order_by('fecha_proxima')
        
        # Agregar días restantes
        for item in vacunas_agendadas:
            if item.fecha_proxima:
                delta = item.fecha_proxima - hoy
                item.dias_restantes = delta.days
        
        for item in productos_agendados:
            if item.fecha_proxima:
                delta = item.fecha_proxima - hoy
                item.dias_restantes = delta.days
        
        context = {
            'vacunas_agendadas': vacunas_agendadas,
            'productos_agendados': productos_agendados,
            'hoy': hoy,
            'total_agendados': vacunas_agendadas.count() + productos_agendados.count()
        }
        
        return render(request, self.template_name, context)


# ============================================================================
# MODIFICACIÓN AL DASHBOARD EXISTENTE
# ============================================================================

@login_required
def dashboard_inventario(request):
    """Vista actualizada para el dashboard de inventario con soporte para agendamiento."""
    
    # Fecha actual para comparaciones
    hoy = timezone.now().date()
    
    # Próximos 30 días para alertas
    fecha_limite = hoy + timedelta(days=30)
    
    # Contadores básicos
    total_vacunas = Vacuna.objects.count()
    total_productos = Producto.objects.count()
    
    # === SEPARAR AGENDADAS DE APLICADAS ===
    
    # Vacunas agendadas (sin aplicar) próximas
    vacunas_agendadas = VacunaAplicada.objects.filter(
        fecha_aplicacion__isnull=True,
        fecha_proxima__lte=fecha_limite
    ).select_related('mascota', 'vacuna').order_by('fecha_proxima')
    
    # Próximas vacunaciones de vacunas YA APLICADAS
    proximas_vacunas_aplicadas = VacunaAplicada.objects.filter(
        fecha_aplicacion__isnull=False,  # Solo las ya aplicadas
        fecha_proxima__lte=fecha_limite
    ).select_related('mascota', 'vacuna').order_by('fecha_proxima')
    
    # Productos agendados (sin aplicar) próximos
    productos_agendados = ProductoAplicado.objects.filter(
        fecha_aplicacion__isnull=True,
        fecha_proxima__lte=fecha_limite
    ).select_related('mascota', 'producto').order_by('fecha_proxima')
    
    # Próximas aplicaciones de productos YA APLICADOS
    proximos_productos_aplicados = ProductoAplicado.objects.filter(
        fecha_aplicacion__isnull=False,  # Solo los ya aplicados
        fecha_proxima__lte=fecha_limite
    ).select_related('mascota', 'producto').order_by('fecha_proxima')
    
    # Agregar días restantes a todos los elementos
    for vacuna in vacunas_agendadas:
        if vacuna.fecha_proxima:
            delta = vacuna.fecha_proxima - hoy
            vacuna.dias_restantes = delta.days
    
    for vacuna in proximas_vacunas_aplicadas:
        if vacuna.fecha_proxima:
            delta = vacuna.fecha_proxima - hoy
            vacuna.dias_restantes = delta.days
    
    for producto in productos_agendados:
        if producto.fecha_proxima:
            delta = producto.fecha_proxima - hoy
            producto.dias_restantes = delta.days
    
    for producto in proximos_productos_aplicados:
        if producto.fecha_proxima:
            delta = producto.fecha_proxima - hoy
            producto.dias_restantes = delta.days
    
    # Estadísticas: Vacunas más aplicadas (solo las realmente aplicadas)
    vacunas_aplicadas = VacunaAplicada.objects.filter(
        fecha_aplicacion__isnull=False
    ).values(
        'vacuna__nombre', 'vacuna_id'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    # Calcular porcentajes para las vacunas más aplicadas
    total_aplicaciones_vacunas = sum(item['count'] for item in vacunas_aplicadas)
    vacunas_populares = []
    
    if total_aplicaciones_vacunas > 0:
        for item in vacunas_aplicadas:
            porcentaje = (item['count'] / total_aplicaciones_vacunas) * 100
            vacunas_populares.append({
                'nombre': item['vacuna__nombre'],
                'count': item['count'],
                'porcentaje': porcentaje
            })
    
    # Estadísticas: Productos más aplicados (solo los realmente aplicados)
    productos_aplicados = ProductoAplicado.objects.filter(
        fecha_aplicacion__isnull=False
    ).values(
        'producto__nombre', 'producto__tipo', 'producto_id'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    # Calcular porcentajes para los productos más aplicados
    total_aplicaciones_productos = sum(item['count'] for item in productos_aplicados)
    productos_populares = []
    
    if total_aplicaciones_productos > 0:
        for item in productos_aplicados:
            porcentaje = (item['count'] / total_aplicaciones_productos) * 100
            productos_populares.append({
                'nombre': item['producto__nombre'],
                'tipo': item['producto__tipo'],
                'count': item['count'],
                'porcentaje': porcentaje,
                'get_tipo_display': 'Vermífugo' if item['producto__tipo'] == 'V' else 'Antiparasitario'
            })
    
    context = {
        'total_vacunas': total_vacunas,
        'total_productos': total_productos,
        
        # Contadores separados
        'vacunas_agendadas_count': vacunas_agendadas.count(),
        'productos_agendados_count': productos_agendados.count(),
        'proximas_vacunaciones_count': proximas_vacunas_aplicadas.count(),
        'proximas_aplicaciones_count': proximos_productos_aplicados.count(),
        
        # Listas detalladas
        'vacunas_agendadas': vacunas_agendadas,
        'productos_agendados': productos_agendados,
        'proximas_vacunas': proximas_vacunas_aplicadas,
        'proximos_productos': proximos_productos_aplicados,
        
        # Estadísticas
        'vacunas_populares': vacunas_populares,
        'productos_populares': productos_populares,
        
        'hoy': hoy.strftime('%Y-%m-%d')
    }
    
    return render(request, 'inventario/dashboard_inventario.html', context)