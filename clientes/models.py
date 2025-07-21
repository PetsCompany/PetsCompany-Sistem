from django.utils import timezone
from django.db import models
from configuracion.models import Especie, Raza
from django.core.validators import RegexValidator

class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="El número debe estar en formato: '+999999999'")]
    )
    correo = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

def ruta_fotos_mascotas(instance, filename):
    # Genera la ruta para guardar la foto: media/mascotas/cliente_id/filename
    return f'mascotas/{instance.cliente.id}/{filename}'

class Mascota(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    
    nombre = models.CharField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='mascotas')
    especie = models.ForeignKey('configuracion.Especie', on_delete=models.PROTECT)
    raza = models.ForeignKey('configuracion.Raza', on_delete=models.PROTECT)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.cliente.nombre})"
    
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        from datetime import date
        today = date.today()
        born = self.fecha_nacimiento
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ['cliente', 'nombre']
        
    def get_ultima_cita(self):
        """
        Obtiene la última cita de la mascota ordenada por fecha y hora
        (independientemente de su estado o fecha)
        """
        return self.citas.order_by('-fecha').first()

    def tiene_citas_completadas(self):
        """
        Verifica si la mascota tiene al menos una cita completada o en curso
        """
        return self.citas.filter(
            fecha__lte=timezone.now().date()
        ).exists()

