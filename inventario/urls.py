from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # URLs para Vacunas #Check
    path('', views.dashboard_inventario, name='dashboard_inventario'),
    path('vacunas/', views.VacunaListView.as_view(), name='lista_vacunas'),
    path('vacunas/crear/', views.VacunaCreateView.as_view(), name='crear_vacuna'),
    path('vacuna/<int:pk>/', views.VacunaDetailView.as_view(), name='detalle_vacuna'),
    path('vacuna/<int:pk>/editar/', views.VacunaUpdateView.as_view(), name='editar_vacuna'), 
    path('vacuna/<int:pk>/eliminar/', views.VacunaDeleteView.as_view(), name='eliminar_vacuna'),
    
    # URLs para Vacunas Aplicadas #Check
    path('mascota/<int:mascota_id>/vacuna/aplicar/', views.VacunaAplicadaCreateView.as_view(), name='aplicar_vacuna'),
    path('vacuna-aplicada/<int:pk>/', views.VacunaAplicadaDetailView.as_view(), name='detalle_vacuna_aplicada'),
    path('vacuna-aplicada/<int:pk>/editar/', views.VacunaAplicadaUpdateView.as_view(), name='editar_vacuna_aplicada'),
    path('vacuna-aplicada/<int:pk>/eliminar/', views.VacunaAplicadaDeleteView.as_view(), name='eliminar_vacuna_aplicada'),
    
    # === NUEVAS URLs PARA SISTEMA DE AGENDAMIENTO DE VACUNAS ===
    # URLs para AGENDAR vacunas (sin aplicar inmediatamente)
    path('mascota/<int:mascota_id>/vacuna/agendar/', views.VacunaAgendadaCreateView.as_view(), name='agendar_vacuna'),
    
    # URLs para APLICAR vacunas que estaban agendadas
    path('vacuna-agendada/<int:pk>/aplicar/', views.AplicarVacunaAgendadaView.as_view(), name='aplicar_vacuna_agendada'),
    
    # URLs para LISTAS de vacunas agendadas
    path('vacunas-agendadas/', views.VacunasAgendadasListView.as_view(), name='vacunas_agendadas'),
    
    # URLs para Productos #Check
    path('productos/', views.ProductoListView.as_view(), name='lista_productos'),
    path('productos/crear/', views.ProductoCreateView.as_view(), name='crear_producto'),
    path('producto/<int:pk>/', views.ProductoDetailView.as_view(), name='detalle_producto'),
    path('producto/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='editar_producto'),
    path('producto/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='eliminar_producto'),
    
    # URLs para Productos Aplicados #Check
    path('mascota/<int:mascota_id>/producto/aplicar/', views.ProductoAplicadoCreateView.as_view(), name='aplicar_producto'),
    path('producto-aplicado/<int:pk>/', views.ProductoAplicadoDetailView.as_view(), name='detalle_producto_aplicado'),
    path('producto-aplicado/<int:pk>/editar/', views.ProductoAplicadoUpdateView.as_view(), name='editar_producto_aplicado'),
    path('producto-aplicado/<int:pk>/eliminar/', views.ProductoAplicadoDeleteView.as_view(), name='eliminar_producto_aplicado'),
    
    # === NUEVAS URLs PARA SISTEMA DE AGENDAMIENTO DE PRODUCTOS ===
    # URLs para AGENDAR productos (sin aplicar inmediatamente)
    path('mascota/<int:mascota_id>/producto/agendar/', views.ProductoAgendadoCreateView.as_view(), name='agendar_producto'),
    
    # URLs para APLICAR productos que estaban agendados
    path('producto-agendado/<int:pk>/aplicar/', views.AplicarProductoAgendadoView.as_view(), name='aplicar_producto_agendado'),
    
    # URLs para LISTAS de productos agendados
    path('productos-agendados/', views.ProductosAgendadosListView.as_view(), name='productos_agendados'),
]