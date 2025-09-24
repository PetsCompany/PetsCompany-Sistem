from django import forms
from .models import Cliente, Mascota
from configuracion.models import Especie, Raza
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'correo', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('correo', css_class='form-group col-md-6 mb-0'),
                Column('direccion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Guardar')
        )

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['cliente', 'nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'foto', 'esterilizado', 'fecha_esterilizacion']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Obtener cliente_id de initial si existe
        initial = kwargs.get('initial', {})
        cliente_id = initial.get('cliente')
        
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        
        # Si hay una instancia con cliente, o se pasó un cliente_id en initial
        if ('instance' in kwargs and kwargs['instance'] is not None and kwargs['instance'].cliente) or cliente_id:
            if 'instance' in kwargs and kwargs['instance'] is not None:
                self.fields['cliente'].initial = kwargs['instance'].cliente
            elif cliente_id:
                self.fields['cliente'].initial = cliente_id
                
            # Ocultar el campo de cliente si ya tenemos uno
            self.fields['cliente'].widget = forms.HiddenInput()
        
        # Configurar el campo de raza inicialmente vacío
        self.fields['raza'].queryset = Raza.objects.none()
        
        # Si ya hay una especie seleccionada, cargar sus razas
        if 'instance' in kwargs and kwargs['instance'] is not None and kwargs['instance'].especie:
            self.fields['raza'].queryset = Raza.objects.filter(especie=kwargs['instance'].especie)
        
        # Si hay datos POST con especie, cargar sus razas
        if 'data' in kwargs and kwargs['data'].get('especie'):
            try:
                especie_id = int(kwargs['data'].get('especie'))
                self.fields['raza'].queryset = Raza.objects.filter(especie_id=especie_id)
            except (ValueError, TypeError):
                pass
        
        self.helper.layout = Layout(
            Row(
                Column('cliente', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('especie', css_class='form-group col-md-6 mb-0'),
                Column('raza', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sexo', css_class='form-group col-md-6 mb-0'),
                Column('fecha_nacimiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'foto',
            Submit('submit', 'Guardar')
        )