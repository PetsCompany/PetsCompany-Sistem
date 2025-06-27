from django import forms
from .models import Vacuna, VacunaAplicada, Producto, ProductoAplicado
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class VacunaForm(forms.ModelForm):
    class Meta:
        model = Vacuna
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'nombre',
            'descripcion',
            Submit('submit', 'Guardar')
        )

class VacunaAplicadaForm(forms.ModelForm):
    class Meta:
        model = VacunaAplicada
        fields = ['mascota', 'vacuna', 'fecha_aplicacion', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Si se proporciona una mascota en initial, pre-establecerla y ocultarla
        if 'initial' in kwargs and 'mascota' in kwargs['initial']:
            self.fields['mascota'].initial = kwargs['initial']['mascota']
            self.fields['mascota'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            'mascota',
            'vacuna',
            Row(
                Column('fecha_aplicacion', css_class='form-group col-md-6 mb-0'),
                Column('fecha_proxima', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'observaciones',
            Submit('submit', 'Guardar')
        )

# ===== NUEVOS FORMULARIOS PARA AGENDAMIENTO =====

class VacunaAgendadaForm(forms.ModelForm):
    """Formulario para AGENDAR vacuna (sin aplicar)"""
    class Meta:
        model = VacunaAplicada
        fields = ['mascota', 'vacuna', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'fecha_proxima': 'Fecha agendada',
            'observaciones': 'Observaciones (opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Si se proporciona una mascota en initial, pre-establecerla y ocultarla
        if 'initial' in kwargs and 'mascota' in kwargs['initial']:
            self.fields['mascota'].initial = kwargs['initial']['mascota']
            self.fields['mascota'].widget = forms.HiddenInput()
        
        # Hacer fecha_proxima obligatoria para agendamiento
        self.fields['fecha_proxima'].required = True
        
        self.helper.layout = Layout(
            'mascota',
            'vacuna',
            'fecha_proxima',
            'observaciones',
            Submit('submit', 'Agendar Vacuna', css_class='btn btn-primary')
        )

class AplicarVacunaAgendadaForm(forms.ModelForm):
    """Formulario para APLICAR una vacuna agendada"""
    class Meta:
        model = VacunaAplicada
        fields = ['fecha_aplicacion', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'fecha_aplicacion': 'Fecha de aplicación',
            'fecha_proxima': 'Próxima dosis (opcional)',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Hacer fecha_aplicacion obligatoria
        self.fields['fecha_aplicacion'].required = True
        
        # Establecer fecha actual por defecto
        from django.utils import timezone
        self.fields['fecha_aplicacion'].initial = timezone.now().date()
        
        self.helper.layout = Layout(
            Row(
                Column('fecha_aplicacion', css_class='form-group col-md-6 mb-0'),
                Column('fecha_proxima', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'observaciones',
            Submit('submit', 'Aplicar Vacuna', css_class='btn btn-success')
        )

# ===== NUEVOS FORMULARIOS PARA PRODUCTOS =====

class ProductoAgendadoForm(forms.ModelForm):
    """Formulario para AGENDAR producto (sin aplicar)"""
    class Meta:
        model = ProductoAplicado
        fields = ['mascota', 'producto', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'fecha_proxima': 'Fecha agendada',
            'observaciones': 'Observaciones (opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Si se proporciona una mascota en initial, pre-establecerla y ocultarla
        if 'initial' in kwargs and 'mascota' in kwargs['initial']:
            self.fields['mascota'].initial = kwargs['initial']['mascota']
            self.fields['mascota'].widget = forms.HiddenInput()
        
        # Hacer fecha_proxima obligatoria para agendamiento
        self.fields['fecha_proxima'].required = True
        
        self.helper.layout = Layout(
            'mascota',
            'producto',
            'fecha_proxima',
            'observaciones',
            Submit('submit', 'Agendar Producto', css_class='btn btn-primary')
        )

class AplicarProductoAgendadoForm(forms.ModelForm):
    """Formulario para APLICAR un producto agendado"""
    class Meta:
        model = ProductoAplicado
        fields = ['fecha_aplicacion', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'fecha_aplicacion': 'Fecha de aplicación',
            'fecha_proxima': 'Próxima dosis (opcional)',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Hacer fecha_aplicacion obligatoria
        self.fields['fecha_aplicacion'].required = True
        
        # Establecer fecha actual por defecto
        from django.utils import timezone
        self.fields['fecha_aplicacion'].initial = timezone.now().date()
        
        self.helper.layout = Layout(
            Row(
                Column('fecha_aplicacion', css_class='form-group col-md-6 mb-0'),
                Column('fecha_proxima', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'observaciones',
            Submit('submit', 'Aplicar Producto', css_class='btn btn-success')
        )

# ===== FORMULARIOS EXISTENTES PARA PRODUCTOS =====

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'tipo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'nombre',
            'tipo',
            'descripcion',
            Submit('submit', 'Guardar')
        )

class ProductoAplicadoForm(forms.ModelForm):
    class Meta:
        model = ProductoAplicado
        fields = ['mascota', 'producto', 'fecha_aplicacion', 'fecha_proxima', 'observaciones']
        widgets = {
            'fecha_aplicacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_proxima': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Si se proporciona una mascota en initial, pre-establecerla y ocultarla
        if 'initial' in kwargs and 'mascota' in kwargs['initial']:
            self.fields['mascota'].initial = kwargs['initial']['mascota']
            self.fields['mascota'].widget = forms.HiddenInput()
        
        self.helper.layout = Layout(
            'mascota',
            'producto',
            Row(
                Column('fecha_aplicacion', css_class='form-group col-md-6 mb-0'),
                Column('fecha_proxima', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'observaciones',
            Submit('submit', 'Guardar')
        )