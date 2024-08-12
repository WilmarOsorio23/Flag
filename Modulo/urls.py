from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),
    path('Tablas', views.Tablas, name='Tablas'),
    path('Tablas/crear', views.crear, name='crear'),
    path('Tablas/editar', views.editar, name='editar'),
    path('Tablas/eliminar', views.eliminar, name='eliminar'),
    path('Tablas/descargar_csv', views.descargar_csv, name='descargar_csv'),
]
