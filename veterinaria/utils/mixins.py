from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea admin"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            if not request.user.perfil.es_admin:
                messages.error(request, "No tienes permisos para realizar esta acción.")
                return redirect('reportes:dashboard') 
        except:
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return redirect('reportes:dashboard')
        
        return super().dispatch(request, *args, **kwargs)

class CanDeleteMixin(LoginRequiredMixin):
    """Mixin para vistas de eliminación - solo usuarios con permisos pueden eliminar"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            if not request.user.perfil.puede_eliminar:
                messages.error(request, "No tienes permisos para eliminar registros.")
                return redirect('reportes:dashboard')
        except AttributeError:
            messages.error(request, "No tienes permisos para eliminar registros.")
            return redirect('reportes:dashboard')
        
        return super().dispatch(request, *args, **kwargs)