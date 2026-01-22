from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("Modulo.urls")),
]

# SOLO en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=getattr(settings, "STATIC_ROOT", None))
    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, "MEDIA_ROOT", None))
