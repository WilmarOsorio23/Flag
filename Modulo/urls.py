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

    # Rutas para tabla IND
    path('ind/', views.ind_index, name='ind_index'),
    path('ind/crear', views.ind_crear, name='ind_crear'),
    path('ind/editar/<int:id>/', views.ind_editar, name='ind_editar'),
    path('ind/eliminar', views.ind_eliminar, name='ind_eliminar'),
    path('ind/descargar_excel', views.ind_descargar_excel, name='ind_descargar_excel'),

    # Rutas para tabla Línea
    path('linea/', views.linea_index, name='linea_index'),
    path('linea/crear', views.linea_crear, name='linea_crear'),
    path('linea/editar/<int:id>/', views.linea_editar, name='linea_editar'),
    path('linea/eliminar', views.linea_eliminar, name='linea_eliminar'),
    path('linea/descargar_excel', views.linea_descargar_excel, name='linea_descargar_excel'),

    # Rutas para tabla Perfil
    path('perfil/', views.perfil_index, name='perfil_index'),
    path('perfil/crear', views.perfil_crear, name='perfil_crear'),
    path('perfil/editar/<int:id>/', views.perfil_editar, name='perfil_editar'),
    path('perfil/eliminar', views.perfil_eliminar, name='perfil_eliminar'),
    path('perfil/descargar_excel', views.perfil_descargar_excel, name='perfil_descargar_excel'),

     # Rutas para tabla TipoDocumento
    path('tipo_documento/', views.tipo_documento_index, name='tipo_documento_index'),
    path('tipo_documento/crear', views.tipo_documento_crear, name='tipo_documento_crear'),
    path('tipo_documento/editar/<int:id>/', views.tipo_documento_editar, name='tipo_documento_editar'),
    path('tipo_documento/eliminar', views.tipo_documento_eliminar, name='tipo_documento_eliminar'),
    path('tipo_documento/descargar_excel', views.tipo_documento_descargar_excel, name='tipo_documento_descargar_excel'),

    # Rutas para la tabla Clientes
    path('clientes/', views.clientes_index, name='clientes_index'),
    path('clientes/crear/', views.clientes_crear, name='clientes_crear'),
    path('clientes/editar/<str:tipo_documento_id>/<str:documento_id>/', views.clientes_editar, name='clientes_editar'),
    path('clientes/eliminar/', views.clientes_eliminar, name='clientes_eliminar'),
    path('clientes/descargar_excel/', views.clientes_descargar_excel, name='clientes_descargar_excel'),

]
