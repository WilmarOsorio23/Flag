from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tu-clave-secreta-muy-segura-para-produccion'  # Cambiar esto por una clave segura

DEBUG = False

ALLOWED_HOSTS = ['web.flagsoluciones.com', 'www.web.flagsoluciones.com']  # Ajusta esto a tu dominio de producción

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'analisisproduc',  # Base de datos de producción
        'USER': 'analisisproduc',   # Usuario de producción
        'PASSWORD': 'Admdev2024.*',  # Contraseña de producción
        'HOST': 'web.flagsoluciones.com',
        'PORT': '3306'
    }
}

# Configuración de archivos estáticos
STATIC_ROOT = '/home/tu_usuario/public_html/static/'
STATIC_URL = '/static/'
MEDIA_ROOT = '/home/tu_usuario/public_html/media/'
MEDIA_URL = '/media/'

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
            'filename': '/home/tu_usuario/logs/django_production.log',
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