from django.db import models
from clientes.models import Mascota
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone 

from django.urls import reverse
from django.conf import settings
import os

class Cita(models.Model):
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField()
    motivo = models.TextField()
    atendida = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Verificar que la mascota esté activa para permitir citas
        if not self.mascota.activa and not self.id:  # Solo para nuevas citas
            raise ValueError("No se pueden agendar citas para mascotas inactivas")
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-fecha']

class Consulta(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='consultas')
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    notas = models.TextField(blank=True, null=True)
    es_eutanasia = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Marcar la cita como atendida solo en la primera consulta
        if not self.cita.atendida:
            self.cita.atendida = True
            self.cita.save()
        
        # Si es eutanasia, marcar la mascota como inactiva
        if self.es_eutanasia:
            mascota = self.cita.mascota
            mascota.activa = False
            mascota.save()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Consulta de {self.cita.mascota.nombre} - {self.fecha_registro.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-fecha_registro']
        
class ImagenDiagnostica(models.Model):
    def upload_to(instance, filename):
        return f'diagnostics/{instance.mascota.id}/{filename}'
        
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='imagenes')
    archivo = models.FileField(upload_to=upload_to)
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Imagen de {self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def get_absolute_url(self):
        return reverse('consultas:detalle_imagen_diagnostica', kwargs={'pk': self.pk})
    
    def is_image(self):
        if self.archivo:
            name = self.archivo.name.lower()
            return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))
        return False
    
    def is_pdf(self):
        if self.archivo:
            return self.archivo.name.lower().endswith('.pdf')
        return False
    
    def is_document(self):
        if self.archivo:
            name = self.archivo.name.lower()
            return name.endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'))
        return False
    
    def get_file_extension(self):
        if self.archivo:
            return self.archivo.name.split('.')[-1].upper()
        return ''
    class Meta:
        verbose_name = "Imagen Diagnóstica"
        verbose_name_plural = "Imágenes Diagnósticas"
        ordering = ['-fecha']