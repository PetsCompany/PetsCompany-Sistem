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
        
from cloudinary.models import CloudinaryField

class ImagenDiagnostica(models.Model):
    def upload_to(instance, filename):
        return f'diagnostics/{instance.mascota.id}/{filename}'
        
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='imagenes')
    
    # Cambiar FileField por CloudinaryField para mejor control
    archivo = CloudinaryField(
        'archivo',
        folder='diagnostics',
        resource_type='auto',  # Esto detecta automáticamente si es imagen o raw
        blank=True,
        null=True
    )
    
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Imagen de {self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def get_absolute_url(self):
        return reverse('consultas:detalle_imagen_diagnostica', kwargs={'pk': self.pk})
    
    def is_image(self):
        if self.archivo:
            name = str(self.archivo).lower()
            return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))
        return False
    
    def is_pdf(self):
        if self.archivo:
            return str(self.archivo).lower().endswith('.pdf')
        return False
    
    def is_document(self):
        if self.archivo:
            name = str(self.archivo).lower()
            return name.endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'))
        return False
    
    def get_file_extension(self):
        if self.archivo:
            return str(self.archivo).split('.')[-1].upper()
        return ''
    
    def get_cloudinary_url(self):
        """Obtiene la URL correcta dependiendo del tipo de archivo"""
        if not self.archivo:
            return ''
        
        url = self.archivo.url
        
        # Si es PDF o documento, cambiar de /image/upload/ a /raw/upload/
        if self.is_pdf() or self.is_document():
            url = url.replace('/image/upload/', '/raw/upload/')
        
        return url
    
    class Meta:
        verbose_name = "Imagen Diagnóstica"
        verbose_name_plural = "Imágenes Diagnósticas"
        ordering = ['-fecha']