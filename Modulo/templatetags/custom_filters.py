from collections import defaultdict
from django import template
from decimal import Decimal, InvalidOperation
import locale

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
def get_dynamic_key(dictionary, base_key):
    """Obtiene valores de claves dinámicas como Cta_Cobro_1, Cta_Cobro_2, etc."""
    if not isinstance(dictionary, dict):
        return None
    
    # Busca todas las claves que coincidan con el patrón
    matching_keys = [k for k in dictionary.keys() if str(k).startswith(base_key)]
    
    # Ordena las claves numéricamente (Cta_Cobro_1, Cta_Cobro_2, etc.)
    matching_keys.sort(key=lambda x: int(x.split('_')[-1]))
    
    # Devuelve lista de valores ordenados
    return [dictionary[key] for key in matching_keys]
    
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

@register.filter
def currency_format(value):
    """Formatea un valor como moneda colombiana con el signo de peso"""
    try:
        if value is None or value == '':
            return '$0'
        
        # Convertir a decimal para manejo seguro
        decimal_value = Decimal(str(value))
        
        # Formatear con separadores de miles y decimales
        formatted = "{:,.0f}".format(decimal_value)
        
        # Agregar el signo de peso
        return f"${formatted}"
    except (ValueError, TypeError, InvalidOperation):
        return '$0'

@register.filter
def currency_format_decimal(value):
    """Formatea un valor como moneda colombiana con decimales"""
    try:
        if value is None or value == '':
            return '$0.00'
        
        # Convertir a decimal para manejo seguro
        decimal_value = Decimal(str(value))
        
        # Formatear con separadores de miles y 2 decimales
        formatted = "{:,.2f}".format(decimal_value)
        
        # Agregar el signo de peso
        return f"${formatted}"
    except (ValueError, TypeError, InvalidOperation):
        return '$0.00'
    
@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def index(list, i):
    try:
        return list[i-1]  # Restamos 1 para que i=1 acceda al índice 0
    except (IndexError, TypeError):
        return None