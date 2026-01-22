import os
from django.core.wsgi import get_wsgi_application

# Si DJANGO_SETTINGS_MODULE ya viene desde ENV, no lo pisa.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "sistema.settings.render")
)

application = get_wsgi_application()
