from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-xg$8kvggebts&j%)(_%!ez(4z9-za&cg28wc98gq(u)din5m(1'

DEBUG = False

ALLOWED_HOSTS = ['gif.flagsoluciones.com']

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
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'Modulo', 'static'),
]
STATIC_ROOT = '/var/www/vhosts/gif.flagsoluciones.com/httpdocs/staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/vhosts/gif.flagsoluciones.com/httpdocs/media'

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
            'filename': 'django_production.log',
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