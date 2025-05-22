from django import forms
from .models import Cita, Consulta, ImagenDiagnostica
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'fecha', 'motivo', 'programada']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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
            Row(
                Column('fecha', css_class='form-group col-md-6 mb-0'),
                Column('programada', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
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
        fields = ['diagnostico', 'tratamiento', 'notas', 'es_eutanasia']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe el diagnóstico realizado...'}),
            'tratamiento': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe el tratamiento aplicado...'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Mejorar etiquetas
        self.fields['diagnostico'].label = 'Diagnóstico'
        self.fields['tratamiento'].label = 'Tratamiento'
        self.fields['notas'].label = 'Notas adicionales'
        self.fields['es_eutanasia'].label = 'Es un procedimiento de eutanasia'
        
        self.helper.layout = Layout(
            'diagnostico',
            'tratamiento',
            'notas',
            'es_eutanasia',
            Submit('submit', 'Guardar Consulta', css_class='btn btn-success')
        )

class ImagenDiagnosticaForm(forms.ModelForm):
    class Meta:
        model = ImagenDiagnostica
        fields = ['mascota', 'archivo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe la imagen diagnóstica...'}),
            'archivo': forms.FileInput(attrs={'accept': 'image/*,.pdf,.doc,.docx'}),
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
        self.fields['archivo'].help_text = 'Formatos permitidos: imágenes, PDF, documentos de Word'
        
        self.helper.layout = Layout(
            'mascota',
            'archivo',
            'descripcion',
            Submit('submit', 'Guardar Imagen', css_class='btn btn-primary')
        )
        
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar tamaño del archivo (máximo 10MB)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo no puede ser mayor a 10MB.")
        return archivo