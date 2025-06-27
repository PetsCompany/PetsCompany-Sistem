from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs existentes
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('cambiar-password/', views.CustomPasswordChangeView.as_view(), name='cambiar_password'),
    path('perfil/', views.PerfilUsuarioView.as_view(), name='perfil'),
    path('configurar-cuenta/', views.ConfigurarCuentaView.as_view(), name='configurar_cuenta'),
    
    # Registro público deshabilitado
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    
    # Nuevas URLs para administración de empleados (solo admin)
    path('empleados/', views.ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('empleados/crear/', views.CrearEmpleadoView.as_view(), name='crear_empleado'),
    path('empleados/editar/<int:user_id>/', views.EditarEmpleadoView.as_view(), name='editar_empleado'),
    path('empleados/cambiar-estado/<int:user_id>/', views.cambiar_estado_empleado, name='cambiar_estado_empleado'),
]