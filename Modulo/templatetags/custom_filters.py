from collections import defaultdict
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario usando una clave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def items(dictionary):
    return dictionary.items()  # Devuelve los items del diccionario

@register.filter
def get_item_safe(dictionary, key):
    if not isinstance(dictionary, dict):
        return {}
    return dictionary.get(key, {})

@register.filter
def get_item3(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def get_item2(value, key):
    """Filtro seguro para obtener valores de diccionarios"""
    try:
        if isinstance(value, (dict, defaultdict)):
            return value.get(key, 0)
        return 0
    except (AttributeError, TypeError):
        return 0
@register.filter
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''
@register.filter
def enumerate_items(iterable):
    return enumerate(iterable)
@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    return float(value) * float(arg)       

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    return float(value) * float(arg)