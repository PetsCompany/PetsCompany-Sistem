from django.contrib import admin
from .models import Cita, Consulta, ImagenDiagnostica

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'fecha', 'motivo')
    #list_filter = ('programada', 'fecha')
    search_fields = ('mascota__nombre', 'motivo')
    date_hierarchy = 'fecha'

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('cita', 'fecha_registro', 'diagnostico', 'es_eutanasia')
    list_filter = ('es_eutanasia', 'fecha_registro')
    search_fields = ('cita__mascota__nombre', 'diagnostico', 'tratamiento')
    date_hierarchy = 'fecha_registro'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['diagnostico'].label = 'Actualización de historia'
        form.base_fields['tratamiento'].label = 'Tratamiento (opcional)'
        return form

@admin.register(ImagenDiagnostica)
class ImagenDiagnosticaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'descripcion', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('mascota__nombre', 'descripcion')
    date_hierarchy = 'fecha'