from django import template

register = template.Library()

@register.filter
def es_admin(user):
    """Verifica si el usuario es admin"""
    try:
        return user.perfil.es_admin
    except:
        return False

@register.filter
def puede_eliminar(user):
    """Verifica si el usuario puede eliminar"""
    try:
        return user.perfil.puede_eliminar
    except:
        return False

@register.filter
def puede_crear_usuarios(user):
    """Verifica si el usuario puede crear usuarios"""
    try:
        return user.perfil.puede_crear_usuarios
    except:
        return False