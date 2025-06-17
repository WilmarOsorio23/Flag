# Este archivo está vacío intencionalmente.
# Su presencia hace que Python trate este directorio como un paquete.

import os

# Determinar qué configuración usar basado en la variable de entorno
environment = os.environ.get('DJANGO_ENV', 'development')

print(f"Cargando configuración de entorno: {environment}")

if environment == 'production':
    from .production import *
elif environment == 'local_production':
    from .local_production import *
else:
    from .development import * 