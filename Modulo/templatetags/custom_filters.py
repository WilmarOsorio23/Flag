from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Devuelve 0 si la clave no existe

@register.filter
def items(dictionary):
    return dictionary.items()  # Devuelve los items del diccionario
