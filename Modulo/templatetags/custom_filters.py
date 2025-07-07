from collections import defaultdict
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def sum_attr(items, attr_name):
    """Suma un atributo específico de una lista de objetos/diccionarios"""
    total = Decimal('0.00')
    for item in items:
        value = item.get(attr_name, Decimal('0.00')) if isinstance(item, dict) else getattr(item, attr_name, Decimal('0.00'))
        try:
            total += Decimal(str(value))
        except (TypeError, ValueError, InvalidOperation):
            continue
    return total

@register.filter
def divide(value, divisor):
    """División segura con manejo de errores"""
    try:
        return Decimal(value) / Decimal(divisor)
    except (TypeError, ValueError, ZeroDivisionError, InvalidOperation):
        return Decimal('0.00')

@register.filter
def multiply(value, multiplier):
    """Multiplicación segura con manejo de errores"""
    try:
        return Decimal(value) * Decimal(multiplier)
    except (TypeError, ValueError, InvalidOperation):
        return Decimal('0.00')

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter
def get_item(dictionary, key):
    try:
        if hasattr(dictionary, 'get'):
            return dictionary.get(key)
        return None
    except Exception:
        return None

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

@register.filter(name='divide')
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    return float(value) * float(arg)