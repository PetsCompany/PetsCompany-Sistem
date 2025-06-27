from django.db import models
from clientes.models import Mascota
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone 

class Cita(models.Model):
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateTimeField()
    motivo = models.TextField()
    programada = models.BooleanField(default=True, help_text="Indica si es una cita programada o atención de urgencia")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    atendida = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
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
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='consulta')
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    notas = models.TextField(blank=True, null=True)
    es_eutanasia = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Marcar la cita como atendida
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
    mascota = models.ForeignKey('clientes.Mascota', on_delete=models.CASCADE, related_name='imagenes')
    archivo = models.FileField(upload_to='imagenes_diagnosticas/%Y/%m/%d/')  # Cambiado de ImageField a FileField
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Imagen de {self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def get_file_type(self):
        """Determina el tipo de archivo basado en la extensión"""
        if self.archivo and self.archivo.name:
            extension = self.archivo.name.lower().split('.')[-1]
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return 'image'
            elif extension == 'pdf':
                return 'pdf'
            elif extension in ['doc', 'docx']:
                return 'document'
            else:
                return 'other'
        return 'unknown'
    
    def is_image(self):
        """Verifica si el archivo es una imagen"""
        return self.get_file_type() == 'image'
    
    class Meta:
        verbose_name = "Imagen Diagnóstica"
        verbose_name_plural = "Imágenes Diagnósticas"
        ordering = ['-fecha']