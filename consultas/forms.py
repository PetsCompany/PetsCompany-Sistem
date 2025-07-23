from django import forms
from .models import Cita, Consulta, ImagenDiagnostica
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'fecha', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Si se proporciona una mascota en initial, pre-establecerla
        if self.initial and 'mascota' in self.initial:
            self.fields['mascota'].initial = self.initial['mascota']
            # Solo hacer readonly si ya hay una mascota seleccionada
            self.fields['mascota'].widget.attrs['readonly'] = True
        
        self.helper.layout = Layout(
            'mascota',
            'fecha',
            'motivo',
            Submit('submit', 'Guardar')
        )
    
    def clean_mascota(self):
        mascota = self.cleaned_data.get('mascota')
        if mascota and not mascota.activa:
            raise forms.ValidationError("No se pueden agendar citas para mascotas inactivas.")
        return mascota

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['diagnostico', 'tratamiento', 'es_eutanasia']  # Removido 'notas'
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe la actualización de la historia clínica...'}),
            'tratamiento': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe el tratamiento aplicado (opcional)...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Mejorar etiquetas - cambiar "diagnóstico" por "Actualización de historia"
        self.fields['diagnostico'].label = 'Actualización de historia'
        self.fields['tratamiento'].label = 'Tratamiento (opcional)'
        self.fields['tratamiento'].required = False  # Hacer tratamiento opcional
        self.fields['es_eutanasia'].label = 'Es un procedimiento de eutanasia'
        
        self.helper.layout = Layout(
            'diagnostico',
            'tratamiento',
            'es_eutanasia',
            Submit('submit', 'Guardar Consulta', css_class='btn btn-success')
        )
    
    def clean_tratamiento(self):
        """Validación personalizada para tratamiento opcional"""
        tratamiento = self.cleaned_data.get('tratamiento', '')
        # Si se proporciona tratamiento, debe tener al menos 10 caracteres
        if tratamiento and len(tratamiento.strip()) < 10:
            raise forms.ValidationError('Si proporciona tratamiento, debe tener al menos 10 caracteres.')
        return tratamiento

class ImagenDiagnosticaForm(forms.ModelForm):
    class Meta:
        model = ImagenDiagnostica
        fields = ['mascota', 'archivo', 'descripcion', 'fecha']  # AGREGAMOS 'fecha'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe la imagen diagnóstica...'}),
            'archivo': forms.FileInput(attrs={
                'accept': 'image/*,.pdf,.doc,.docx',
                'class': 'form-control'
            }),
            'fecha': forms.DateTimeInput(attrs={  # NUEVO WIDGET
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        
        # Si se proporciona una mascota en initial, pre-establecerla y ocultarla
        if self.initial and 'mascota' in self.initial:
            self.fields['mascota'].initial = self.initial['mascota']
            self.fields['mascota'].widget = forms.HiddenInput()
        
        # Mejorar etiquetas y placeholder
        self.fields['archivo'].label = 'Archivo diagnóstico'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['fecha'].label = 'Fecha del estudio'  # NUEVA ETIQUETA
        self.fields['archivo'].help_text = 'Formatos permitidos: imágenes (JPG, PNG, GIF), PDF, documentos de Word. Máximo 10MB'
        
        self.helper.layout = Layout(
            'mascota',
            'archivo',
            'descripcion',
            'fecha',  # AGREGAMOS AL LAYOUT
            Submit('submit', 'Guardar Imagen', css_class='btn btn-primary')
        )
        
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño del archivo (máximo 10MB)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo no puede ser mayor a 10MB.")
            
            # Validar extensión de archivo
            allowed_extensions = [
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',  # Imágenes
                'pdf',  # PDF
                'doc', 'docx'  # Documentos Word
            ]
            
            file_extension = archivo.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"Tipo de archivo no permitido. "
                    f"Extensiones permitidas: {', '.join(allowed_extensions)}"
                )
                
        return archivo