from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),

    # Rutas para tabla Modulo
    path('Modulo', views.modulo, name='Modulo'),
    path('Modulo/crear', views.crear, name='crear'),
    path('Modulo/editar/<int:id>/', views.editar, name='editar'),
    path('Modulo/eliminar', views.eliminar, name='eliminar'),
    path('Modulo/descargar_excel', views.descargar_excel, name='descargar_excel'),

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

    # Rutas para la tabla Consultores
    path('consultores/', views.consultores_index, name='consultores_index'),
    path('consultores/crear/', views.consultores_crear, name='consultores_crear'),
    path('consultores/editar/<str:tipo_documento_id>/<str:documento_id>/', views.consultores_editar, name='consultores_editar'),
    path('consultores/eliminar/', views.consultores_eliminar, name='consultores_eliminar'),
    path('consultores/descargar_excel/', views.consultores_descargar_excel, name='consultores_descargar_excel'),

    # Rutas para tabla Certificacion
    path('certificacion/', views.certificacion_index, name='certificacion_index'),
    path('certificacion/crear', views.certificacion_crear, name='certificacion_crear'),
    path('certificacion/editar/<int:id>/', views.certificacion_editar, name='certificacion_editar'),
    path('certificacion/eliminar', views.certificacion_eliminar, name='certificacion_eliminar'),
    path('certificacion/descargar_excel', views.certificacion_descargar_excel, name='certificacion_descargar_excel'),
    
    # Rutas para tabla Costos Indirecto
    path('costos_indirectos/', views.costos_indirectos_index, name='costos_indirectos_index'),
    path('costos_indirectos/crear', views.costos_indirectos_crear, name='costos_indirectos_crear'),
    path('costos_indirectos/editar/<int:id>/', views.costos_indirectos_editar, name='costos_indirectos_editar'),
    path('costos_indirectos/eliminar', views.costos_indirectos_eliminar, name='costos_indirectos_eliminar'),
    path('costos_indirectos/descargar_excel', views.costos_indirectos_descargar_excel, name='costos_indirectos_descargar_excel'),

    # Rutas para la tabla Concepto
    path('conceptos/', views.conceptos_index, name='conceptos_index'),
    path('conceptos/crear', views.conceptos_crear, name='conceptos_crear'),
    path('conceptos/editar/<int:id>/', views.conceptos_editar, name='conceptos_editar'),
    path('conceptos/eliminar', views.conceptos_eliminar, name='conceptos_eliminar'),
    path('conceptos/descargar_excel', views.conceptos_descargar_excel, name='conceptos_descargar_excel'),

    # Rutas para tabla Gastos
    path('gastos/', views.gasto_index, name='gastos_index'),
    path('gastos/crear', views.gasto_crear, name='gastos_crear'),
    path('gastos/editar/<int:id>/', views.gasto_editar, name='gastos_editar'),
    path('gastos/eliminar', views.gasto_eliminar, name='gastos_eliminar'),
    path('gastos/descargar_excel', views.gasto_descargar_excel, name='gastos_descargar_excel'),

    # Rutas para tabla Detalle de Gastos
    path('detalle_gastos/', views.detalle_gastos_index, name='detalle_gastos_index'),
    path('detalle_gastos/crear', views.detalle_gastos_crear, name='detalle_gastos_crear'),
    path('detalle_gastos/editar/<str:Anio>/<str:Mes>/<int:GastosId>/', views.detalle_gastos_editar, name='detalle_gastos_editar'),
    path('detalle_gastos/eliminar', views.detalle_gastos_eliminar, name='detalle_gastos_eliminar'),
    path('detalle_gastos/descargar_excel', views.detalle_gastos_descargar_excel, name='detalle_gastos_descargar_excel'),

    # Rutas para tabla Total de Gastos
    path('total_gastos/', views.total_gastos_index, name='total_gastos_index'),
    path('total_gastos/crear', views.total_gastos_crear, name='total_gastos_crear'),
    path('total_gastos/editar/<str:anio>/<str:mes>/', views.total_gastos_editar, name='total_gastos_editar'),
    path('total_gastos/eliminar', views.total_gastos_eliminar, name='total_gastos_eliminar'),
    path('total_gastos/descargar_excel', views.total_gastos_descargar_excel, name='total_gastos_descargar_excel'),

    # Rutas para tabla Total Costos Indirectos
    path('total_costos_indirectos/', views.total_costos_indirectos_index, name='total_costos_indirectos_index'),
    path('total_costos_indirectos/crear/', views.total_costos_indirectos_crear, name='total_costos_indirectos_crear'),
    path('total_costos_indirectos/editar/<str:anio>/<str:mes>/', views.total_costos_indirectos_editar, name='total_costos_indirectos_editar'),
    path('total_costos_indirectos/eliminar/', views.total_costos_indirectos_eliminar, name='total_costos_indirectos_eliminar'),
    path('total_costos_indirectos/descargar_excel/', views.total_costos_indirectos_descargar_excel, name='total_costos_indirectos_descargar_excel'),

    # Rutas para tabla Detalle Costos Indirectos
    path('detalle_costos_indirectos/', views.detalle_costos_indirectos_index, name='detalle_costos_indirectos_index'),
    path('detalle_costos_indirectos/crear', views.detalle_costos_indirectos_crear, name='detalle_costos_indirectos_crear'),
    path('detalle_costos_indirectos/editar/<int:id>/', views.detalle_costos_indirectos_editar, name='detalle_costos_indirectos_editar'),
    path('detalle_costos_indirectos/eliminar', views.detalle_costos_indirectos_eliminar, name='detalle_costos_indirectos_eliminar'),
    path('detalle_costos_indirectos/descargar_excel', views.detalle_costos_indirectos_descargar_excel, name='detalle_costos_indirectos_descargar_excel'),

    # Rutas para tabla Tiempos Concepto
    path('tiempos_concepto/', views.tiempos_concepto_index, name='tiempos_concepto_index'),
    path('tiempos_concepto/crear', views.tiempos_concepto_crear, name='tiempos_concepto_crear'),
    path('tiempos_concepto/editar/<str:id>/', views.tiempos_concepto_editar, name='tiempos_concepto_editar'),
    path('tiempos_concepto/eliminar', views.tiempos_concepto_eliminar, name='tiempos_concepto_eliminar'),
    path('tiempos_concepto/descargar_excel', views.tiempos_concepto_descargar_excel, name='tiempos_concepto_descargar_excel'),

    # Rutas para tabla Tiempos Cliente
    path('tiempos_cliente/', views.tiempos_cliente_index, name='tiempos_cliente_index'),
    path('tiempos_cliente/crear', views.tiempos_cliente_crear, name='tiempos_cliente_crear'),
    path('tiempos_cliente/editar/<int:id>/', views.tiempos_cliente_editar, name='tiempos_cliente_editar'),
    path('tiempos_cliente/eliminar', views.tiempos_cliente_eliminar, name='tiempos_cliente_eliminar'),
    path('tiempos_cliente/descargar_excel', views.tiempos_cliente_descargar_excel, name='tiempos_cliente_descargar_excel'),

    # Rutas para tabla Nomina
    path('nomina/', views.nomina_index, name='nomina_index'),
    path('nomina/crear', views.nomina_crear, name='nomina_crear'),
    path('nomina/editar/<str:anio>/<str:mes>/<str:documento>/', views.nomina_editar, name='nomina_editar'),
    path('nomina/eliminar', views.nomina_eliminar, name='nomina_eliminar'),
    path('nomina/descargar_excel', views.nomina_descargar_excel, name='nomina_descargar_excel'),

    # Rutas para tabla Detalle Certificación
    path('detalle_certificacion/', views.detalle_certificacion_index, name='detalle_certificacion_index'),
    path('detalle_certificacion/crear/', views.detalle_certificacion_crear, name='detalle_certificacion_crear'),
    path('detalle_certificacion/editar/<str:documentoId>/<str:certificacionId>/', views.detalle_certificacion_editar, name='detalle_certificacion_editar'),
    path('detalle_certificacion/eliminar/', views.detalle_certificacion_eliminar, name='detalle_certificacion_eliminar'),
    path('detalle_certificacion/descargar_excel/', views.detalle_certificacion_descargar_excel, name='detalle_certificacion_descargar_excel'),

    # Rutas para la tabla Empleado
    path('empleado/', views.empleado_index, name='empleado_index'),
    path('empleado/crear/', views.empleado_crear, name='empleado_crear'),
    path('empleado/editar/<str:tipo_documento_id>/<str:documento_id>/', views.empleado_editar, name='empleado_editar'),
    path('empleado/eliminar/', views.empleado_eliminar, name='empleado_eliminar'),
    path('empleado/descargar_excel/', views.empleado_descargar_excel, name='empleado_descargar_excel'),

    # Rutas para informe de certificación
    path('informes/', views.empleado_filtrado, name='informes_certificacion_index'),
    path('informes/salarios/', views.empleado_nomina_filtrado, name='informes_salarios_index'),
    path('descargar_excel/', views.descargar_excel, name='descargar_excel'),
]
