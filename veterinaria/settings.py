import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dtdrwrcbf",
    api_key="485393467686619",
    api_secret="Sv3sSne2UD0cp9d14Jt5b8Lnd8g", 
    secure=True
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración segura para producción
SECRET_KEY = os.getenv("SECRET_KEY", "clave-insegura-en-desarrollo")
DEBUG = os.getenv("DEBUG", "False") == "True"
if not DEBUG:
    USE_SECURE_MEDIA = True
    
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'petscompany.up.railway.app',  # Tu dominio exacto
    '*.railway.app',  # Para subdominios de Railway
]

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary apps
    'cloudinary_storage',
    'cloudinary',
    
    # Apps propias
    'usuarios.apps.UsuariosConfig',
    'clientes.apps.ClientesConfig',
    'consultas.apps.ConsultasConfig',
    'inventario.apps.InventarioConfig',
    'reportes.apps.ReportesConfig',
    'configuracion.apps.ConfiguracionConfig',
    'portal_cliente.apps.PortalClienteConfig',

    # Apps de terceros
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # necesario para static en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'veterinaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'veterinaria.wsgi.application'

# Base de datos
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}",
        conn_max_age=600,
        ssl_require=True if not DEBUG else False  # SSL solo en producción
    )
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuración internacional
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Solo usar WhiteNoise storage en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos de usuario (subidas)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if not DEBUG:  # Solo en producción
    # Usar un servidor web como nginx para servir archivos estáticos
    # pero si necesitas que Django los sirva temporalmente:
    SECURE_MEDIA_URL = '/media/'

# Configuración de formularios
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Redirecciones de login/logout
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'reportes:dashboard'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# Email (para recordatorios, desactivado por defecto)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración específica para Railway
CSRF_TRUSTED_ORIGINS = [
    "https://petscompany.up.railway.app"
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://petscompany.up.railway.app',  #dominio exacto con https
    'https://*.railway.app',  # Para cualquier subdominio de Railway
]

# Configuración de cookies para producción
CSRF_COOKIE_SECURE = True  # Solo HTTPS en producción
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_AGE = 3600  # 1 hora

# Configuración de sesión
SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 semanas

# Headers de proxy para Railway
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Si estás en desarrollo local, mantén configuración menos restrictiva
if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    ALLOWED_HOSTS.extend(['127.0.0.1:8000', 'localhost:8000'])
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ])
    
# Configuración de archivos media
# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dtdrwrcbf',
    'API_KEY': '485393467686619',
    'API_SECRET': 'Sv3sSne2UD0cp9d14Jt5b8Lnd8g',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'