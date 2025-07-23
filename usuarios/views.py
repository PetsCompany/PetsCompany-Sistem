from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView, ListView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
import re
from .models import PerfilUsuario
from django.views.generic.edit import CreateView
from .forms import RegistroUsuarioForm, CrearEmpleadoForm

# Mixin para verificar permisos de admin
class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea admin"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar si tiene perfil y es admin
        try:
            if not request.user.perfil.es_admin:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect('reportes:dashboard')
        except PerfilUsuario.DoesNotExist:
            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect('reportes:dashboard')
        
        return super().dispatch(request, *args, **kwargs)

class CustomUserForm(forms.ModelForm):
    """Formulario personalizado para editar datos del usuario"""
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su apellido'
        })
    )
    email = forms.EmailField(
        required=False,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verificar que no exista otro usuario con el mismo email (excluyendo el actual)
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing_user.exists():
                raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email


class PerfilUsuarioForm(forms.ModelForm):
    """Formulario para el perfil del usuario"""
    telefono = forms.CharField(
        max_length=15,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 123-456-7890'
        })
    )
    cargo = forms.CharField(
        max_length=100,
        required=False,
        label='Cargo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Veterinario Principal'
        })
    )
    
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'cargo']
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar el teléfono de caracteres no numéricos para validación
            numeros_solo = re.sub(r'\D', '', telefono)
            if len(numeros_solo) < 7 or len(numeros_solo) > 15:
                raise ValidationError("El teléfono debe tener entre 7 y 15 números.")
        return telefono


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f"¡Bienvenido/a {form.get_user().get_full_name() or form.get_user().username}!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('reportes:dashboard')


class CustomLogoutView(LogoutView):
    next_page = 'usuarios:login'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, f"Hasta luego, {request.user.get_full_name() or request.user.username}. Has cerrado sesión exitosamente.")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(AdminRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/cambiar_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('usuarios:perfil')
    
    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña ha sido actualizada exitosamente.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrige los errores en el formulario.")
        return super().form_invalid(form)


class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar el perfil del usuario"""
    template_name = 'usuarios/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Obtener o crear perfil si no existe
        perfil, created = PerfilUsuario.objects.get_or_create(user=self.request.user)
        context['perfil'] = perfil
        
        # Si se creó un nuevo perfil, informar al usuario
        if created:
            messages.info(self.request, "Se ha creado tu perfil. Puedes actualizarlo con tu información personal.")
        
        return context


class ConfigurarCuentaView(LoginRequiredMixin, TemplateView):
    """Vista para configurar la cuenta del usuario"""
    template_name = 'usuarios/configurar_cuenta.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener o crear perfil
        perfil, created = PerfilUsuario.objects.get_or_create(user=self.request.user)
        
        # Crear formularios
        context['user_form'] = CustomUserForm(instance=self.request.user)
        context['perfil_form'] = PerfilUsuarioForm(instance=perfil)
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Obtener o crear perfil
        perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
        
        # Crear formularios con datos del POST
        user_form = CustomUserForm(request.POST, instance=request.user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        
        # Validar ambos formularios
        if user_form.is_valid() and perfil_form.is_valid():
            # Guardar información del usuario
            user = user_form.save()
            
            # Guardar información del perfil
            perfil = perfil_form.save(commit=False)
            perfil.user = user
            perfil.save()
            
            messages.success(request, "Tu información ha sido actualizada exitosamente.")
            return redirect('usuarios:perfil')
        else:
            # Si hay errores, mostrar mensaje y renderizar formulario con errores
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            
            # Preparar context con formularios que contienen errores
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['perfil_form'] = perfil_form
            
            return self.render_to_response(context)

# REGISTRO PÚBLICO - SE DESHABILITA
class RegistroUsuarioView(CreateView):
    """Vista deshabilitada - Solo admins pueden crear usuarios"""
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/signup.html'
    success_url = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        # Deshabilitar registro público
        messages.error(request, "El registro público está deshabilitado. Contacta al administrador para crear tu cuenta.")
        return redirect('usuarios:login')

# NUEVAS VISTAS PARA ADMINISTRACIÓN DE EMPLEADOS

class CrearEmpleadoView(AdminRequiredMixin, CreateView):
    """Vista para que el admin cree empleados"""
    form_class = CrearEmpleadoForm
    template_name = 'usuarios/crear_empleado.html'
    success_url = reverse_lazy('usuarios:lista_empleados')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Empleado {form.instance.get_full_name()} creado exitosamente.")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Por favor corrige los errores en el formulario.")
        return super().form_invalid(form)


class ListaEmpleadosView(AdminRequiredMixin, ListView):
    """Vista para listar todos los empleados"""
    model = User
    template_name = 'usuarios/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 20
    
    def get_queryset(self):
        # Solo mostrar usuarios que tienen perfil
        return User.objects.filter(perfil__isnull=False).select_related('perfil').order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Los perfiles ya incluyen password_visible, no hay que hacer nada más
        return context

class EditarEmpleadoView(AdminRequiredMixin, TemplateView):
    """Vista para editar empleados"""
    template_name = 'usuarios/editar_empleado.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # Crear formularios iniciales
        context['empleado'] = user
        context['user_form'] = CustomUserForm(instance=user)
        
        # Obtener o crear perfil
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        context['perfil_form'] = PerfilUsuarioForm(instance=perfil)
        
        # Formulario para cambiar rol (solo si no es el usuario actual)
        if user != self.request.user:
            context['puede_cambiar_rol'] = True
            context['rol_actual'] = perfil.rol
        
        return context
    
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        
        user_form = CustomUserForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            
            # Cambiar rol si se especificó y no es el usuario actual
            if user != request.user and 'rol' in request.POST:
                nuevo_rol = request.POST.get('rol')
                if nuevo_rol in ['admin', 'veterinario']:
                    perfil.rol = nuevo_rol
                    perfil.save()
            
            messages.success(request, f"Información de {user.get_full_name()} actualizada exitosamente.")
            return redirect('usuarios:lista_empleados')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['perfil_form'] = perfil_form
            return self.render_to_response(context)


def cambiar_estado_empleado(request, user_id):
    """Vista AJAX para activar/desactivar empleados"""
    if not request.user.is_authenticated or not request.user.perfil.es_admin:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # No permitir desactivar al propio usuario
        if user == request.user:
            return JsonResponse({'success': False, 'error': 'No puedes desactivar tu propia cuenta'})
        
        # Cambiar estado
        user.is_active = not user.is_active
        user.save()
        
        accion = "activado" if user.is_active else "desactivado"
        messages.success(request, f"Usuario {user.get_full_name()} {accion} exitosamente.")
        
        return JsonResponse({
            'success': True, 
            'nuevo_estado': user.is_active,
            'mensaje': f"Usuario {accion} exitosamente"
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})