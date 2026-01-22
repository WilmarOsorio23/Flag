from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

def healthz(_request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path("healthz", healthz),
    path("admin/", admin.site.urls),
    path("", include("modulo.urls")),
] + static(settings.STATIC_URL, document_root=getattr(settings, "STATIC_ROOT", None)) + static(settings.MEDIA_URL, document_root=getattr(settings, "MEDIA_ROOT", None))
