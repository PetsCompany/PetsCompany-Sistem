from django.db import models
from django.core.exceptions import ValidationError
from clientes.models import Mascota

class Vacuna(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"
        ordering = ['nombre']

class VacunaAplicada(models.Model):
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='vacunas_aplicadas')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.PROTECT)
    # CAMBIO PRINCIPAL: Hacer fecha_aplicacion opcional
    fecha_aplicacion = models.DateField(blank=True, null=True)  # Era obligatorio
    fecha_proxima = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    @property
    def es_agendada(self):
        """Retorna True si la vacuna está agendada (sin aplicar)"""
        return self.fecha_aplicacion is None and self.fecha_proxima is not None

    @property
    def es_aplicada(self):
        """Retorna True si la vacuna ya fue aplicada"""
        return self.fecha_aplicacion is not None

    @property
    def estado_display(self):
        """Retorna el estado en formato legible"""
        if self.es_agendada:
            return "Agendada"
        elif self.es_aplicada:
            return "Aplicada"
        return "Sin estado"

    @property
    def fecha_principal(self):
        """Devuelve la fecha más relevante para mostrar"""
        return self.fecha_aplicacion or self.fecha_proxima

    def clean(self):
        """Validaciones personalizadas"""
        if not self.fecha_aplicacion and not self.fecha_proxima:
            raise ValidationError("Debe especificar al menos una fecha (aplicación o próxima)")
    
    def __str__(self):
        if self.fecha_aplicacion:
            fecha_display = self.fecha_aplicacion.strftime('%d/%m/%Y')
        else:
            fecha_display = f"Agendada: {self.fecha_proxima.strftime('%d/%m/%Y')}" if self.fecha_proxima else "Sin fecha"
        return f"{self.vacuna.nombre} - {self.mascota.nombre} ({fecha_display})"
    
    def save(self, *args, **kwargs):
        # Verificar que la mascota esté activa
        if not self.mascota.activa and not self.id:  # Solo para nuevos registros
            raise ValueError("No se pueden aplicar vacunas a mascotas inactivas")
        
        # Ejecutar validaciones personalizadas
        self.clean()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Vacuna Aplicada"
        verbose_name_plural = "Vacunas Aplicadas"
        ordering = ['-fecha_aplicacion', '-fecha_proxima']  # Ordenar por ambas fechas

class Producto(models.Model):
    TIPO_CHOICES = [
        ('V', 'Vermífugo'),
        ('A', 'Antiparasitario'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

class ProductoAplicado(models.Model):
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='productos_aplicados')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    # CAMBIO PRINCIPAL: Hacer fecha_aplicacion opcional
    fecha_aplicacion = models.DateField(blank=True, null=True)  # Era obligatorio
    fecha_proxima = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    @property
    def es_agendado(self):
        """Retorna True si el producto está agendado (sin aplicar)"""
        return self.fecha_aplicacion is None and self.fecha_proxima is not None

    @property
    def es_aplicado(self):
        """Retorna True si el producto ya fue aplicado"""
        return self.fecha_aplicacion is not None

    @property
    def estado_display(self):
        """Retorna el estado en formato legible"""
        if self.es_agendado:
            return "Agendado"
        elif self.es_aplicado:
            return "Aplicado"
        return "Sin estado"

    @property
    def fecha_principal(self):
        """Devuelve la fecha más relevante para mostrar"""
        return self.fecha_aplicacion or self.fecha_proxima

    def clean(self):
        """Validaciones personalizadas"""
        if not self.fecha_aplicacion and not self.fecha_proxima:
            raise ValidationError("Debe especificar al menos una fecha (aplicación o próxima)")
    
    def __str__(self):
        if self.fecha_aplicacion:
            fecha_display = self.fecha_aplicacion.strftime('%d/%m/%Y')
        else:
            fecha_display = f"Agendado: {self.fecha_proxima.strftime('%d/%m/%Y')}" if self.fecha_proxima else "Sin fecha"
        return f"{self.producto.nombre} - {self.mascota.nombre} ({fecha_display})"
    
    def save(self, *args, **kwargs):
        # Verificar que la mascota esté activa
        if not self.mascota.activa and not self.id:  # Solo para nuevos registros
            raise ValueError("No se pueden aplicar productos a mascotas inactivas")
        
        # Ejecutar validaciones personalizadas
        self.clean()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Producto Aplicado"
        verbose_name_plural = "Productos Aplicados"
        ordering = ['-fecha_aplicacion', '-fecha_proxima']  # Ordenar por ambas fechas