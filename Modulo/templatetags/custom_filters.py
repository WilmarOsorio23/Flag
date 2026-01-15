# Modulo/templatetags/custom_filters.py
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
    return dictionary.items()

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

    matching_keys = [k for k in dictionary.keys() if str(k).startswith(base_key)]
    matching_keys.sort(key=lambda x: int(x.split('_')[-1]))
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

# ====== IMPORTANTE: tenías estos filtros duplicados en tu archivo original ======
# Los dejo UNA sola vez para evitar comportamientos raros en templates.

@register.filter(name='divide')
def divide_float(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter(name='multiply')
def multiply_float(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='has_permission')
def has_permission(user, permission):
    """
    Template filter to check if a user has a specific permission through their role.
    Usage: {% if user|has_permission:'can_manage_modulo' %}
    """
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True

    role = getattr(user, "role", None)
    if not role:
        return False

    return bool(getattr(role, permission, False))

# ====== OPCIONAL: para simplificar ifs gigantes en templates ======
@register.filter(name='has_any_permission')
def has_any_permission(user, perms_csv: str):
    """
    Usage:
      {% if user|has_any_permission:"perm1,perm2,perm3" %} ... {% endif %}
    """
    perms = [p.strip() for p in (perms_csv or "").split(",") if p.strip()]
    return any(has_permission(user, p) for p in perms)

@register.filter
def currency_format(value):
    """Formatea un valor como moneda colombiana con el signo de peso"""
    try:
        if value is None or value == '':
            return '$0'
        decimal_value = Decimal(str(value))
        formatted = "{:,.0f}".format(decimal_value)
        return f"${formatted}"
    except (ValueError, TypeError, InvalidOperation):
        return '$0'

@register.filter
def currency_format_decimal(value):
    """Formatea un valor como moneda colombiana con decimales"""
    try:
        if value is None or value == '':
            return '$0.00'
        decimal_value = Decimal(str(value))
        formatted = "{:,.2f}".format(decimal_value)
        return f"${formatted}"
    except (ValueError, TypeError, InvalidOperation):
        return '$0.00'

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def index(lst, i):
    try:
        return lst[i-1]
    except (IndexError, TypeError):
        return None
