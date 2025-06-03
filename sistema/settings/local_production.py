from .production import *

# Mensaje de debug para mostrar la configuración
print("\n=== Configuración de Base de Datos ===")
print(f"Nombre de BD: {DATABASES['default']['NAME']}")
print(f"Usuario: {DATABASES['default']['USER']}")
print(f"Host: {DATABASES['default']['HOST']}")
print("=====================================\n")

# Permitir acceso local
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Desactivar configuraciones de seguridad SSL ya que estamos en local
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Mantener la configuración de archivos estáticos local
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'Modulo', 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de logging local
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_local_production.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
} 