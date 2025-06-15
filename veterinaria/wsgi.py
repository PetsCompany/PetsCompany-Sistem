"""
WSGI config for veterinaria project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinaria.settings')

# Ejecutar migraciones automáticamente
django.setup()
from django.core.management import call_command
try:
    call_command('migrate')
except Exception as e:
    print(f"Error en migraciones: {e}")

application = get_wsgi_application()
call_command('collectstatic', '--noinput')