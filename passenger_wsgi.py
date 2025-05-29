import sys, os

# Configuración de directorios
VENV_NAME = 'venv'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(PROJECT_ROOT, VENV_NAME)
VENV_PYTHON = os.path.join(VENV_PATH, 'bin', 'python')

# Activar el entorno virtual
if sys.executable != VENV_PYTHON:
    os.execl(VENV_PYTHON, VENV_PYTHON, *sys.argv)

# Añadir rutas al path de Python
sys.path.insert(0, PROJECT_ROOT)

# Configurar el entorno de desarrollo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings.development')

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 