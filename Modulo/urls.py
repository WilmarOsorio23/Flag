from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),
    path('Tablas', views.Tablas, name='Tablas'),
    path('Tablas/crear', views.crear, name='crear'),
    path('Tablas/editar/<int:id>/', views.editar, name='editar'),
    path('Tablas/eliminar', views.eliminar, name='eliminar'),
    path('Tablas/descargar_excel', views.descargar_excel, name='descargar_excel'),
]
