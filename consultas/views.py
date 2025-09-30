from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from clientes.models import Mascota
from .models import Cita, Consulta, ImagenDiagnostica
from .forms import CitaForm, ConsultaForm, ImagenDiagnosticaForm
from inventario.models import VacunaAplicada, ProductoAplicado
from veterinaria.utils.mixins import CanDeleteMixin
from django.http import HttpResponse, Http404, FileResponse
from django.views.decorators.cache import cache_control
import mimetypes
import os
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator


class CitaListView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = 'consultas/lista_citas.html'
    context_object_name = 'citas'
    ordering = ['-fecha']
    paginate_by = 10  # Paginación para citas

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por fecha si se proporciona en la URL
        fecha_filtro = self.request.GET.get('fecha')
        
        if fecha_filtro:
            queryset = queryset.filter(fecha=fecha_filtro)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener vacunas agendadas (sin aplicar)
        vacunas_agendadas = VacunaAplicada.objects.filter(
            fecha_aplicacion__isnull=True,
            fecha_proxima__isnull=False,
            mascota__activa=True
        ).select_related('mascota', 'vacuna', 'mascota__cliente').order_by('fecha_proxima')
        
        # Obtener productos agendados (sin aplicar)
        productos_agendados = ProductoAplicado.objects.filter(
            fecha_aplicacion__isnull=True,
            fecha_proxima__isnull=False,
            mascota__activa=True
        ).select_related('mascota', 'producto', 'mascota__cliente').order_by('fecha_proxima')
        
        # APLICAR FILTROS ANTES DE PAGINAR
        fecha_filtro = self.request.GET.get('fecha')
        if fecha_filtro:
            try:
                fecha_obj = timezone.datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                vacunas_agendadas = vacunas_agendadas.filter(fecha_proxima=fecha_obj)
                productos_agendados = productos_agendados.filter(fecha_proxima=fecha_obj)
            except ValueError:
                pass
        
        # CONTAR ANTES DE PAGINAR
        total_vacunas = vacunas_agendadas.count()
        total_productos = productos_agendados.count()
        #total_citas_pendientes = context['citas'].filter(atendida=False).count()
        
        # Paginación para vacunas (DESPUÉS del filtro)
        vacunas_paginator = Paginator(vacunas_agendadas, 10)
        vacunas_page = self.request.GET.get('vacunas_page', 1)
        vacunas_paginadas = vacunas_paginator.get_page(vacunas_page)
        
        # Paginación para productos (DESPUÉS del filtro)
        productos_paginator = Paginator(productos_agendados, 10)
        productos_page = self.request.GET.get('productos_page', 1)
        productos_paginados = productos_paginator.get_page(productos_page)
        
        context.update({
            'vacunas_agendadas': vacunas_paginadas,
            'productos_agendados': productos_paginados,
            #'total_pendientes': total_citas_pendientes + total_vacunas + total_productos
        })
        
        return context


class CitaDetailView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = 'consultas/detalle_cita.html'
    context_object_name = 'cita'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        consultas = self.object.consultas.all().order_by('-fecha_registro')
        context['consultas'] = consultas
        return context


class CitaCreateView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'consultas/cita_form.html'
    success_url = reverse_lazy('consultas:lista_citas')
    
    def get_initial(self):
        initial = super().get_initial()
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            initial['mascota'] = mascota
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            form.instance.mascota = mascota
        
        messages.success(self.request, "Consulta programada creada exitosamente.")
        return super().form_valid(form)


class CitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'consultas/cita_form.html'
    
    def get_success_url(self):
        return reverse_lazy('consultas:detalle_cita', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Consulta programada actualizada exitosamente.")
        return super().form_valid(form)


class CitaDeleteView(CanDeleteMixin, DeleteView):
    model = Cita
    template_name = 'consultas/confirmar_eliminar_cita.html'
    success_url = reverse_lazy('consultas:lista_citas')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Consulta programada eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vistas para Consultas
class ConsultaCreateView(LoginRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'consultas/consulta_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cita_id = self.kwargs.get('cita_id')
        cita = get_object_or_404(Cita, pk=cita_id)
        context['cita'] = cita
        
        # Detectar desde dónde viene el usuario
        from_param = self.request.GET.get('from', 'nueva_consulta')
        context['from_actualizar_historia'] = (from_param == 'actualizar_historia')
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        cita_id = self.kwargs.get('cita_id')
        cita = get_object_or_404(Cita, pk=cita_id)
            
        form.instance.cita = cita
        
        messages.success(self.request, "Consulta registrada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('consultas:detalle_cita', kwargs={'pk': self.kwargs.get('cita_id')})


class ConsultaDetailView(LoginRequiredMixin, DetailView):
    model = Consulta
    template_name = 'consultas/detalle_consulta.html'
    context_object_name = 'consulta'


class ConsultaUpdateView(LoginRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'consultas/consulta_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cita'] = self.object.cita
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        # Verificar si cambió el estado de eutanasia
        consulta = self.get_object()
        mascota = consulta.cita.mascota
        
        # Si ahora es eutanasia y antes no lo era
        if form.cleaned_data.get('es_eutanasia') and not consulta.es_eutanasia:
            mascota.activa = False
            mascota.save()
        # Si ahora NO es eutanasia pero antes lo era
        elif not form.cleaned_data.get('es_eutanasia') and consulta.es_eutanasia:
            mascota.activa = True
            mascota.save()
        
        messages.success(self.request, "Consulta actualizada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('consultas:detalle_consulta', kwargs={'pk': self.object.pk})


class ConsultaDeleteView(CanDeleteMixin, DeleteView):
    model = Consulta
    template_name = 'consultas/confirmar_eliminar_consulta.html'
    
    def get_success_url(self):
        cita_id = self.object.cita.id
        return reverse_lazy('consultas:detalle_cita', kwargs={'pk': cita_id})
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        consulta = self.get_object()
        cita = consulta.cita
        
        # Si era una eutanasia, reactivar la mascota
        if consulta.es_eutanasia:
            mascota = cita.mascota
            mascota.activa = True
            mascota.save()
        
        # Marcar la cita como no atendida solo si no hay más consultas
        if cita.consultas.count() == 1:  # Solo esta consulta
            cita.atendida = False
            cita.save()
        
        messages.success(self.request, "Consulta eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# Vista para la historia clínica - Esta vista combina datos de varias tablas
class HistoriaClinicaView(LoginRequiredMixin, View):
    template_name = 'consultas/historia_clinica.html'
    
    def get(self, request, mascota_id):
        mascota = get_object_or_404(Mascota, pk=mascota_id)
        
        # Obtener consultas con select_related para optimizar
        consultas = Consulta.objects.filter(
            cita__mascota=mascota
        ).select_related('cita').order_by('-cita__fecha')
        
        # Obtener vacunas aplicadas
        vacunas_aplicadas = VacunaAplicada.objects.filter(
            mascota=mascota
        ).select_related('vacuna').order_by('-fecha_aplicacion')
        
        # Obtener productos aplicados
        productos_aplicados = ProductoAplicado.objects.filter(
            mascota=mascota
        ).select_related('producto').order_by('-fecha_aplicacion')
        
        # Obtener imágenes diagnósticas
        imagenes_diagnosticas = ImagenDiagnostica.objects.filter(
            mascota=mascota
        ).order_by('-fecha')
        
        # Crear línea de tiempo unificada
        eventos = self.get_unified_timeline(consultas, vacunas_aplicadas, productos_aplicados, imagenes_diagnosticas)
        
        context = {
            'mascota': mascota,
            'consultas': consultas,
            'vacunas_aplicadas': vacunas_aplicadas,
            'productos_aplicados': productos_aplicados,
            'imagenes_diagnosticas': imagenes_diagnosticas,
            'eventos': eventos,
        }
        return render(request, self.template_name, context)
    
    def get_unified_timeline(self, consultas, vacunas_aplicadas, productos_aplicados, imagenes_diagnosticas):
        eventos = []

        # Agregar consultas
        for consulta in consultas:
            # Verificar que la cita y la fecha existen
            if consulta.cita and consulta.cita.fecha:
                # Convertir datetime a date para comparación consistente
                fecha = consulta.cita.fecha.date() if hasattr(consulta.cita.fecha, 'date') else consulta.cita.fecha
                fecha_str = consulta.cita.fecha.strftime('%d/%m/%Y') if consulta.cita.fecha else 'Sin fecha'
                eventos.append({
                    'fecha': fecha,
                    'tipo': 'consulta',
                    'objeto': consulta,
                    'titulo': f'Consulta - {fecha_str}'
                })
        
        # Agregar vacunas
        for vacuna in vacunas_aplicadas:
            if vacuna.fecha_aplicacion:
                # fecha_aplicacion ya debería ser date, pero verificamos por seguridad
                fecha = vacuna.fecha_aplicacion.date() if hasattr(vacuna.fecha_aplicacion, 'date') else vacuna.fecha_aplicacion
                eventos.append({
                    'fecha': fecha,
                    'tipo': 'vacuna',
                    'objeto': vacuna,
                    'titulo': f'Vacuna: {vacuna.vacuna.nombre}'
                })
        
        # Agregar productos
        for producto in productos_aplicados:
            if producto.fecha_aplicacion:
                # fecha_aplicacion ya debería ser date, pero verificamos por seguridad
                fecha = producto.fecha_aplicacion.date() if hasattr(producto.fecha_aplicacion, 'date') else producto.fecha_aplicacion
                eventos.append({
                    'fecha': fecha,
                    'tipo': 'producto',
                    'objeto': producto,
                    'titulo': f'Producto: {producto.producto.nombre}'
                })
            
        # Agregar imágenes diagnósticas
        for imagen in imagenes_diagnosticas:
            if imagen.fecha:
                # Manejar tanto date como datetime
                fecha = imagen.fecha.date() if hasattr(imagen.fecha, 'date') else imagen.fecha
                descripcion = imagen.descripcion[:50] + '...' if imagen.descripcion and len(imagen.descripcion) > 50 else (imagen.descripcion or 'Sin descripción')
                eventos.append({
                    'fecha': fecha,
                    'tipo': 'imagen',
                    'objeto': imagen,
                    'titulo': f'Imagen diagnóstica: {descripcion}'
                })
        
        # Ordenar por fecha descendente, manejando posibles valores None
        eventos.sort(key=lambda x: x['fecha'] if x['fecha'] else timezone.now().date(), reverse=True)
        return eventos

@login_required
def historia_clinica_imprimible(request, mascota_id):
    """
    Vista para generar la versión imprimible de la historia clínica
    """
    mascota = get_object_or_404(Mascota, id=mascota_id)
    
    # Obtener todos los datos relacionados
    consultas = Consulta.objects.filter(
        cita__mascota=mascota
    ).select_related('cita').order_by('-cita__fecha')
    
    vacunas_aplicadas = VacunaAplicada.objects.filter(
        mascota=mascota
    ).select_related('vacuna').order_by('-fecha_aplicacion')
    
    productos_aplicados = ProductoAplicado.objects.filter(
        mascota=mascota
    ).select_related('producto').order_by('-fecha_aplicacion')
    
    imagenes_diagnosticas = ImagenDiagnostica.objects.filter(
        mascota=mascota
    ).order_by('-fecha')
    
    context = {
        'mascota': mascota,
        'consultas': consultas,
        'vacunas_aplicadas': vacunas_aplicadas,
        'productos_aplicados': productos_aplicados,
        'imagenes_diagnosticas': imagenes_diagnosticas,
    }
    
    return render(request, 'consultas/historia_clinica_print.html', context)


@method_decorator(login_required, name='dispatch')
class HistoriaClinicaImprimibleView(DetailView):
    """
    Vista basada en clase para la historia clínica imprimible
    """
    model = Mascota
    template_name = 'consultas/historia_clinica_print.html'
    context_object_name = 'mascota'
    pk_url_kwarg = 'mascota_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota = self.get_object()
        
        # Obtener historial médico
        context['consultas'] = Consulta.objects.filter(
            cita__mascota=mascota
        ).select_related('cita').order_by('-cita__fecha')
        
        context['vacunas_aplicadas'] = VacunaAplicada.objects.filter(
            mascota=mascota
        ).select_related('vacuna').order_by('-fecha_aplicacion')
        
        context['productos_aplicados'] = ProductoAplicado.objects.filter(
            mascota=mascota
        ).select_related('producto').order_by('-fecha_aplicacion')
        
        context['imagenes_diagnosticas'] = ImagenDiagnostica.objects.filter(
            mascota=mascota
        ).order_by('-fecha')
        
        return context

# Vistas para Imágenes Diagnósticas
class ImagenDiagnosticaListView(LoginRequiredMixin, ListView):
    model = ImagenDiagnostica
    template_name = 'consultas/lista_imagenes_diagnosticas.html'
    context_object_name = 'imagenes'
    paginate_by = 12
    
    def get_queryset(self):
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            return ImagenDiagnostica.objects.filter(mascota=mascota).order_by('-fecha')
        return ImagenDiagnostica.objects.select_related(
            'mascota__cliente'
        ).order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        return context


class ImagenDiagnosticaCreateView(LoginRequiredMixin, CreateView):
    model = ImagenDiagnostica
    form_class = ImagenDiagnosticaForm
    template_name = 'consultas/imagen_diagnostica_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            initial['mascota'] = mascota
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            context['mascota'] = get_object_or_404(Mascota, pk=mascota_id)
        return context
    
    def form_valid(self, form):
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            form.instance.mascota = mascota
        
        messages.success(self.request, "Imagen diagnóstica guardada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            return reverse_lazy('consultas:lista_imagenes_diagnosticas_mascota', kwargs={'mascota_id': mascota_id})
        return reverse_lazy('consultas:lista_imagenes_diagnosticas')


class ImagenDiagnosticaDetailView(LoginRequiredMixin, DetailView):
    model = ImagenDiagnostica
    template_name = 'consultas/detalle_imagen_diagnostica.html'
    context_object_name = 'imagen'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.archivo:
            context['has_file'] = True
            context['is_image'] = self.object.is_image()
            context['is_pdf'] = self.object.is_pdf()
            context['is_document'] = self.object.is_document()
            context['file_extension'] = self.object.get_file_extension()
            context['archivo_url'] = self.object.get_cloudinary_url() 
        else:
            context['has_file'] = False
            context['is_image'] = False
            context['is_pdf'] = False
            context['is_document'] = False
            context['archivo_url'] = ''
        return context


class ImagenDiagnosticaUpdateView(LoginRequiredMixin, UpdateView):
    model = ImagenDiagnostica
    form_class = ImagenDiagnosticaForm
    template_name = 'consultas/imagen_diagnostica_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['mascota'] = self.object.mascota
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mascota'] = self.object.mascota
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Imagen diagnóstica actualizada exitosamente.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('consultas:lista_imagenes_diagnosticas_mascota', 
                          kwargs={'mascota_id': self.object.mascota.pk})


class ImagenDiagnosticaDeleteView(LoginRequiredMixin, DeleteView):  # Removido CanDeleteMixin por simplicidad
    model = ImagenDiagnostica
    template_name = 'consultas/confirmar_eliminar_imagen.html'
    context_object_name = 'imagen'
    
    def get_success_url(self):
        return reverse_lazy('consultas:lista_imagenes_diagnosticas_mascota', 
                          kwargs={'mascota_id': self.object.mascota.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Imagen diagnóstica eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)