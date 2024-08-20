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

    # Rutas para la tabla IPC
    path('ipc/', views.ipc_index, name='ipc_index'),
    path('ipc/crear', views.ipc_crear, name='ipc_crear'),
    path('ipc/editar/<int:id>/', views.ipc_editar, name='ipc_editar'),
    path('ipc/eliminar', views.ipc_eliminar, name='ipc_eliminar'),
    path('ipc/descargar_excel', views.ipc_descargar_excel, name='ipc_descargar_excel'),

    # Rutas para la tabla Clientes
    path('clientes/', views.clientes_index, name='clientes_index'),
    path('clientes/crear/', views.clientes_crear, name='clientes_crear'),
    path('clientes/editar/<str:tipo_documento_id>/<str:documento_id>/', views.clientes_editar, name='clientes_editar'),
    path('clientes/eliminar/', views.clientes_eliminar, name='clientes_eliminar'),
    path('clientes/descargar_excel/', views.clientes_descargar_excel, name='clientes_descargar_excel'),

]
