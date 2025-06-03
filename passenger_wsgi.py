import sys, os

# Configuración de la aplicación
ApplicationDirectory = '/'
ApplicationName = 'sistema'
VirtualEnvDirectory = 'venv'

# Configuración del entorno virtual
VirtualEnv = os.path.join(os.getcwd(), VirtualEnvDirectory, 'bin', 'python')
if sys.executable != VirtualEnv: 
    os.execl(VirtualEnv, VirtualEnv, *sys.argv)

# Configuración de rutas
sys.path.insert(0, os.path.join(os.getcwd(), ApplicationDirectory))
sys.path.insert(0, os.path.join(os.getcwd(), ApplicationDirectory, ApplicationName))
sys.path.insert(0, os.path.join(os.getcwd(), VirtualEnvDirectory, 'bin'))

# Cambiar al directorio de la aplicación
os.chdir(os.path.join(os.getcwd(), ApplicationDirectory))

# Configurar el módulo de settings según el dominio
if 'devgif.flagsoluciones.com' in os.getcwd():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings.production')

# Importar y configurar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 