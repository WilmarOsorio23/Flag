import os
import sys

# Añade la ruta del proyecto al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configura las variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings.production')

# Importa la aplicación WSGI
from sistema.wsgi import application 