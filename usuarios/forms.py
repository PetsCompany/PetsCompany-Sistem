from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PerfilUsuario

# Formulario original se mantiene pero solo para admins
class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

# Nuevo formulario para que el admin cree empleados
class CrearEmpleadoForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña',
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña'
    )
    
    # Campos del perfil
    telefono = forms.CharField(
        max_length=15,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cargo = forms.CharField(
        max_length=100,
        required=False,
        label='Cargo',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROLE_CHOICES,
        initial='veterinario',
        label='Rol',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Las contraseñas no coinciden.")
            if len(password) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password_texto_plano = self.cleaned_data['password']  # NUEVO: Guardar antes de encriptar
        user.set_password(password_texto_plano)  # Esto encripta la contraseña
        
        if commit:
            user.save()
            # Crear o actualizar el perfil
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.cargo = self.cleaned_data.get('cargo', '')
            perfil.rol = self.cleaned_data.get('rol', 'veterinario')
            perfil.password_visible = password_texto_plano  # NUEVO: Guardar contraseña visible
            perfil.save()
        
        return user