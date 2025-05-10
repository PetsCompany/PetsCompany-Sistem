from django.contrib import admin
from .models import Vacuna, VacunaAplicada, Producto, ProductoAplicado

@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(VacunaAplicada)
class VacunaAplicadaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'vacuna', 'fecha_aplicacion', 'fecha_proxima')
    list_filter = ('vacuna', 'fecha_aplicacion')
    search_fields = ('mascota__nombre', 'vacuna__nombre')
    date_hierarchy = 'fecha_aplicacion'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descripcion')
    list_filter = ('tipo',)
    search_fields = ('nombre',)

@admin.register(ProductoAplicado)
class ProductoAplicadoAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'producto', 'fecha_aplicacion', 'fecha_proxima')
    list_filter = ('producto', 'fecha_aplicacion')
    search_fields = ('mascota__nombre', 'producto__nombre')
    date_hierarchy = 'fecha_aplicacion'