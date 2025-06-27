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