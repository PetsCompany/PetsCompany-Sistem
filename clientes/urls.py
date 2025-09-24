from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # URLs para Clientes #Check
    path('', views.ClienteListView.as_view(), name='lista_clientes'),
    path('crear/', views.ClienteCreateView.as_view(), name='crear_cliente'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detalle_cliente'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar_cliente'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='eliminar_cliente'),
    
    # URLs para Mascotas #Check
    path('mascotas/', views.MascotaListView.as_view(), name='lista_mascotas'),
    path('cliente/<int:cliente_id>/mascotas/', views.MascotaListView.as_view(), name='mascotas_por_cliente'), #falta integracion # No es necesario
    path('cliente/<int:cliente_id>/mascota/crear/', views.MascotaCreateView.as_view(), name='crear_mascota'),
    path('mascota/<int:pk>/', views.MascotaDetailView.as_view(), name='detalle_mascota'),
    path('mascota/<int:pk>/editar/', views.MascotaUpdateView.as_view(), name='editar_mascota'),
    path('mascota/<int:pk>/eliminar/', views.MascotaDeleteView.as_view(), name='eliminar_mascota'),
    path('mascotas/cumpleanos/', views.MascotasCumpleanosView.as_view(), name='cumpleanos_mascotas'),
    
    # API endpoint para obtener razas por especie #Check
    path('get_razas_by_especie/', views.get_razas_by_especie, name='get_razas_by_especie'),
]