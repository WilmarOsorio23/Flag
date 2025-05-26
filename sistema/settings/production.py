from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tu-clave-secreta-muy-segura-para-produccion'  # Cambiar esto por una clave segura

DEBUG = False

ALLOWED_HOSTS = ['web.flagsoluciones.com']  # Ajusta esto a tu dominio de producción

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'analisis_prod',  # Base de datos de producción
        'USER': 'usuario_prod',   # Usuario de producción
        'PASSWORD': 'contraseña_prod',  # Contraseña de producción
        'HOST': 'web.flagsoluciones.com',
        'PORT': '3306'
    }
}

# Configuración de archivos estáticos
STATIC_ROOT = '/var/www/static/'
STATIC_URL = '/static/'

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/production.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
} 