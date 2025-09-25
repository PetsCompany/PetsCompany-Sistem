from django.urls import path
from . import views

app_name = 'consultas'

urlpatterns = [
    # URLs para Citas #Check
    path('citas/', views.CitaListView.as_view(), name='lista_citas'),
    path('citas/crear/', views.CitaCreateView.as_view(), name='crear_cita'),
    path('mascota/<int:mascota_id>/cita/crear/', views.CitaCreateView.as_view(), name='crear_cita_mascota'), #No hace falta #No implementada 
    path('cita/<int:pk>/', views.CitaDetailView.as_view(), name='detalle_cita'), 
    path('cita/<int:pk>/editar/', views.CitaUpdateView.as_view(), name='editar_cita'),
    path('cita/<int:pk>/eliminar/', views.CitaDeleteView.as_view(), name='eliminar_cita'),
    
    # URLs para Consultas #Check
    path('cita/<int:cita_id>/consulta/crear/', views.ConsultaCreateView.as_view(), name='crear_consulta'),
    path('consulta/<int:pk>/', views.ConsultaDetailView.as_view(), name='detalle_consulta'),
    path('consulta/<int:pk>/editar/', views.ConsultaUpdateView.as_view(), name='editar_consulta'),
    path('consulta/<int:pk>/eliminar/', views.ConsultaDeleteView.as_view(), name='eliminar_consulta'),
    
    # URL para Historia Clínica #Check
    path('mascota/<int:mascota_id>/historia-clinica/', views.HistoriaClinicaView.as_view(), name='historia_clinica'),
    path('mascota/<int:mascota_id>/historia-clinica/imprimir/v2/', views.HistoriaClinicaImprimibleView.as_view(), name='historia_clinica_imprimible_v2'),    
    
    # URLs para Imágenes Diagnósticas #Check
    path('imagenes/', views.ImagenDiagnosticaListView.as_view(), name='lista_imagenes_diagnosticas'),# No hace falta #Falla
    path('mascota/<int:mascota_id>/imagenes/', views.ImagenDiagnosticaListView.as_view(), name='lista_imagenes_diagnosticas_mascota'),
    path('mascota/<int:mascota_id>/imagenes/nueva/', views.ImagenDiagnosticaCreateView.as_view(), name='crear_imagen_diagnostica_mascota'),
    path('imagen/<int:pk>/', views.ImagenDiagnosticaDetailView.as_view(), name='detalle_imagen_diagnostica'),
    path('imagen/<int:pk>/editar/', views.ImagenDiagnosticaUpdateView.as_view(), name='editar_imagen_diagnostica'),
    path('imagen/<int:pk>/eliminar/', views.ImagenDiagnosticaDeleteView.as_view(), name='eliminar_imagen_diagnostica'),

]