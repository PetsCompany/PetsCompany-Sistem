from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from clientes.models import Mascota
from .models import Cita, Consulta, ImagenDiagnostica
from .forms import CitaForm, ConsultaForm, ImagenDiagnosticaForm
from inventario.models import VacunaAplicada, ProductoAplicado
from veterinaria.utils.mixins import CanDeleteMixin


# Vistas para Citas
class CitaListView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = 'consultas/lista_citas.html'
    context_object_name = 'citas'
    ordering = ['-fecha']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por fecha si se proporciona en la URL
        fecha_filtro = self.request.GET.get('fecha')
        estado_filtro = self.request.GET.get('estado')
        
        if fecha_filtro:
            queryset = queryset.filter(fecha__date=fecha_filtro)
            
        if estado_filtro == 'atendida':
            queryset = queryset.filter(atendida=True)
        elif estado_filtro == 'pendiente':
            queryset = queryset.filter(atendida=False)
            
        return queryset


class CitaDetailView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = 'consultas/detalle_cita.html'
    context_object_name = 'cita'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Comprobar si hay una consulta asociada a esta cita
        try:
            consulta = Consulta.objects.get(cita=self.object)
            context['consulta'] = consulta
        except Consulta.DoesNotExist:
            context['consulta'] = None
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
        
        messages.success(self.request, "Cita creada exitosamente.")
        return super().form_valid(form)


class CitaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'consultas/cita_form.html'
    
    def get_success_url(self):
        return reverse_lazy('consultas:detalle_cita', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Cita actualizada exitosamente.")
        return super().form_valid(form)


class CitaDeleteView(CanDeleteMixin, DeleteView):
    model = Cita
    template_name = 'consultas/confirmar_eliminar_cita.html'
    success_url = reverse_lazy('consultas:lista_citas')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cita eliminada exitosamente.")
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
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        cita_id = self.kwargs.get('cita_id')
        cita = get_object_or_404(Cita, pk=cita_id)
        
        # Verificar que no exista ya una consulta para esta cita
        if hasattr(cita, 'consulta'):
            messages.error(self.request, "Esta cita ya tiene una consulta registrada.")
            return redirect('consultas:detalle_cita', pk=cita.id)
            
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
        
        # Marcar la cita como no atendida
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
            # Convertir datetime a date para comparación consistente
            fecha = consulta.cita.fecha.date() if hasattr(consulta.cita.fecha, 'date') else consulta.cita.fecha
            eventos.append({
                'fecha': fecha,
                'tipo': 'consulta',
                'objeto': consulta,
                'titulo': f'Consulta - {consulta.cita.fecha.strftime("%d/%m/%Y")}'
            })
        
        # Agregar vacunas
        for vacuna in vacunas_aplicadas:
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
            # Manejar tanto date como datetime
            fecha = imagen.fecha.date() if hasattr(imagen.fecha, 'date') else imagen.fecha
            eventos.append({
                'fecha': fecha,
                'tipo': 'imagen',
                'objeto': imagen,
                'titulo': f'Imagen diagnóstica: {imagen.descripcion[:50]}...'
            })
        
        # Ordenar por fecha descendente
        eventos.sort(key=lambda x: x['fecha'], reverse=True)
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
    paginate_by = 12  # Mostrar 12 imágenes por página
    
    def get_queryset(self):
        mascota_id = self.kwargs.get('mascota_id')
        if mascota_id:
            mascota = get_object_or_404(Mascota, pk=mascota_id)
            # No necesitamos select_related aquí ya que tenemos la mascota
            return ImagenDiagnostica.objects.filter(mascota=mascota).order_by('-fecha')
        # Para la vista general, sí necesitamos select_related
        return ImagenDiagnostica.objects.select_related(
            'mascota__propietario'
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
        # Si no hay mascota_id, redirigir a la lista general
        return reverse_lazy('consultas:lista_imagenes_diagnosticas')


class ImagenDiagnosticaDetailView(LoginRequiredMixin, DetailView):
    model = ImagenDiagnostica
    template_name = 'consultas/detalle_imagen_diagnostica.html'
    context_object_name = 'imagen'


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


class ImagenDiagnosticaDeleteView(CanDeleteMixin, DeleteView):
    model = ImagenDiagnostica
    template_name = 'consultas/confirmar_eliminar_imagen.html'
    context_object_name = 'imagen'
    
    def get_success_url(self):
        return reverse_lazy('consultas:lista_imagenes_diagnosticas_mascota', 
                          kwargs={'mascota_id': self.object.mascota.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Imagen diagnóstica eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)