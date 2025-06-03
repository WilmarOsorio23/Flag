from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-03wz*^i+6am@4m6_--r7()a429+u&rq8o=e38p*(druigcq1t)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'devgif.flagsoluciones.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'analisisdev',
        'USER': 'analisisdev',
        'PASSWORD': 'Admdev2024.*',
        'HOST': 'web.flagsoluciones.com',
        'PORT': '3306'
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'Modulo', 'static'),
]
STATIC_ROOT = '/var/www/vhosts/devgif.flagsoluciones.com/httpdocs/staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/vhosts/devgif.flagsoluciones.com/httpdocs/media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_debug.log',
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