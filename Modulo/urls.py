from django.urls import path
from Modulo.Views import Act_Maestro, Informe_clientes, clientes_factura, indicadores_operatividad, indicadores_totales, informe_facturacion_clientes, informe_tiempos_consultores, modulo
from Modulo.Views import ipc
from Modulo.Views import ind
from Modulo.Views import TipoDocumento
from Modulo.Views import Certificacion
from Modulo.Views import Conceptos
from Modulo.Views import Clientes
from Modulo.Views import CostosIndirectos
from Modulo.Views import gastos
from Modulo.Views import cargos
from Modulo.Views import empleado_nomina_filtrado
from Modulo.Views import informe_empleados
from Modulo.Views import informe_estudios  
from Modulo.Views import informe_consultores
from Modulo.Views import informe_tarifas_consultores
from Modulo.Views import informe_tarifas_clientes
from Modulo.Views import informe_clientes_contratos
from Modulo.Views import informe_otros_si
from Modulo.Views import empleado
from Modulo.Views import consultores
from Modulo.Views import Nomina
from Modulo.Views import Informe_certificaciones
from Modulo.Views.Informe_Pagare import exportar_pagares_excel, informe_pagares
from Modulo.Views.Pagare import actualizar_pagare, eliminar_pagares, guardar_pagare, obtener_datos_pagares, obtener_pagares_empleado, pag_ejecutado, pag_planeado, pagare_index
from Modulo.Views.TipoPagare import tipo_pagare_confirmar_delete, tipo_pagare_crear, tipo_pagare_descargar_excel, tipo_pagare_editar, tipo_pagare_eliminar, tipo_pagare_index
from Modulo.models import TiposContactos
from Modulo.views import ActividadPagare
from . import views
from Modulo.Views import perfil
from Modulo.Views import linea
from Modulo.Views import detallesCostosIndirectos
from Modulo.Views import detallesCertificacion
from Modulo.Views import detalleGastos
from Modulo.Views import totalGasto
from Modulo.Views import totalCostos
from Modulo.Views import tiposContactos
from Modulo.Views import contactos
from Modulo.Views import historial_cargos
from Modulo.Views import empleados_estudios
from Modulo.Views import registro_tiempos
from Modulo.Views import Horas_Habiles
from Modulo.Views import tarifa_consultores
from Modulo.Views import moneda
from Modulo.Views import clientes_Contratos
from Modulo.Views import ContratosOtrosSi
from Modulo.Views import tarifa_Clientes
from Modulo.Views import referencia
from Modulo.Views import centrosCostos
from Modulo.Views import informe_facturacion
from Modulo.Views import informe_historial_cargos
from Modulo.Views import indicadores_facturacion
from Modulo.Views import indicadores_margen_cliente

from Modulo.Views import facturacion_consultores
from Modulo.Views import informe_facturacion_consultores
from Modulo.Views import informe_serv_consultor



urlpatterns = [
    # Auth URLs
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Role management
    path('roles/', auth_views.role_list, name='role_list'),
    path('roles/create/', auth_views.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', auth_views.role_edit, name='role_edit'),
    
    # User management
    path('users/', auth_views.user_list, name='user_list'),
    path('users/create/', auth_views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', auth_views.user_edit, name='user_edit'),
    
    # Permission check endpoint
    path('check-permission/', auth_views.check_permission, name='check_permission'),

    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),

    # Rutas para tabla Modulo
    path('Modulo', modulo.modulo, name='Modulo'),
    path('Modulo/crear', modulo.crear, name='crear'),
    path('Modulo/editar/<int:id>/', modulo.editar, name='editar'),
    path('Modulo/eliminar', modulo.eliminar, name='eliminar'),
    path('verificar-relaciones/', modulo.verificar_relaciones, name='verificar_relaciones'),
    path('Modulo/descargar_excel', modulo.descargar_excel, name='descargar_excel'),

    # Rutas para tabla Moneda
    path('moneda/', moneda.moneda_index, name='moneda_index'),
    path('moneda/crear', moneda.moneda_crear, name='moneda_crear'),
    path('moneda/editar/<int:id>/', moneda.moneda_editar, name='moneda_editar'),
    path('moneda/eliminar', moneda.moneda_eliminar, name='moneda_eliminar'),
    path('moneda/verificar-relaciones/', moneda.verificar_relaciones, name='verificar_relaciones'),
    path('moneda/descargar_excel', moneda.moneda_descargar_excel, name='moneda_descargar_excel'),

    # Rutas para la tabla IPC
    path('ipc/', ipc.ipc_index, name='ipc_index'),
    path('ipc/crear', ipc.ipc_crear, name='ipc_crear'),
    path('ipc/editar/<int:id>/', ipc.ipc_editar, name='ipc_editar'),
    path('ipc/eliminar', ipc.ipc_eliminar, name='ipc_eliminar'),
    path('ipc/descargar_excel', ipc.ipc_descargar_excel, name='ipc_descargar_excel'),

    # Rutas para tabla IND
    path('ind/', ind.ind_index, name='ind_index'),
    path('ind/crear', ind.ind_crear, name='ind_crear'),
    path('ind/editar/<int:id>/', ind.ind_editar, name='ind_editar'),
    path('ind/eliminar', ind.ind_eliminar, name='ind_eliminar'),
    path('ind/descargar_excel', ind.ind_descargar_excel, name='ind_descargar_excel'),

    # Rutas para tabla Línea
    path('linea/', linea.linea_index, name='linea_index'),
    path('linea/crear', linea.linea_crear, name='linea_crear'),
    path('linea/editar/<int:id>/', linea.linea_editar, name='linea_editar'),
    path('linea/verificar-relaciones/', linea.verificar_relaciones, name='verificar_relaciones'),
    path('linea/eliminar', linea.linea_eliminar, name='linea_eliminar'),
    path('linea/descargar_excel', linea.linea_descargar_excel, name='linea_descargar_excel'),

    # Rutas para tabla Perfil
    path('perfil/', perfil.perfil_index, name='perfil_index'),
    path('perfil/crear', perfil.perfil_crear, name='perfil_crear'),
    path('perfil/editar/<int:id>/', perfil.perfil_editar, name='perfil_editar'),
    path('verificar-relaciones/', perfil.verificar_relaciones, name='verificar_relaciones'),
    path('perfil/eliminar', perfil.perfil_eliminar, name='perfil_eliminar'),
    path('perfil/descargar_excel', perfil.perfil_descargar_excel, name='perfil_descargar_excel'),

     # Rutas para tabla TipoDocumento
    path('tipo_documento/', TipoDocumento.tipo_documento_index, name='tipo_documento_index'),
    path('tipo_documento/crear', TipoDocumento.tipo_documento_crear, name='tipo_documento_crear'),
    path('tipo_documento/editar/<int:id>/', TipoDocumento.tipo_documento_editar, name='tipo_documento_editar'),
    path('tipo_documento/verificar-relaciones/', TipoDocumento.verificar_relaciones, name='verificar_relaciones'),
    path('tipo_documento/eliminar', TipoDocumento.tipo_documento_eliminar, name='tipo_documento_eliminar'),
    path('tipo_documento/descargar_excel', TipoDocumento.tipo_documento_descargar_excel, name='tipo_documento_descargar_excel'),

    # Rutas para tabla Modulo
    path('Cargos/', cargos.cargos_index, name='cargos_index'),
    path('Cargos/crear', cargos.crear, name='cargos_crear'),
    path('Cargos/editar/<int:id>/', cargos.editar, name='cargos_editar'),
    path('Cargos/eliminar', cargos.eliminar, name='cargos_eliminar'),
    path('Cargos/verificar-relaciones/', cargos.verificar_relaciones, name='cargos_verificar_relaciones'),
    path('Cargos/descargar_excel', cargos.descargar_excel, name='cargos_descargar_excel'),

    # Rutas para la tabla Clientes
    path('clientes/', Clientes.clientes_index, name='clientes_index'),
    path('clientes/crear/', Clientes.clientes_crear, name='clientes_crear'),
    path('clientes/editar/<int:id>/', Clientes.clientes_editar, name='clientes_editar'),
    path('clientes/eliminar/', Clientes.clientes_eliminar, name='clientes_eliminar'),
    path('clientes/verificar-relaciones/', Clientes.verificar_relaciones, name='clientes_verificar_relaciones'),
    path('clientes/descargar_excel/', Clientes.clientes_descargar_excel, name='clientes_descargar_excel'),
    path('clientes/contactos/', Clientes.obtener_contactos, name='obtener_contactos'),# Nueva ruta para obtener contactos

    # Rutas para la tabla Consultores
    path('consultores/', consultores.consultores_index, name='consultores_index'),
    path('consultores/crear/', consultores.consultores_crear, name='consultores_crear'),
    path('consultores/editar/<str:id>/', consultores.consultores_editar, name='consultores_editar'),
    path('consultores/eliminar/', consultores.consultores_eliminar, name='consultores_eliminar'),
    path('consultores/verificar-relaciones/', consultores.verificar_relaciones, name='consultores_verificar_relaciones'),
    path('consultores/descargar_excel/', consultores.consultores_descargar_excel, name='consultores_descargar_excel'),

    #Ruta para tabla Actividades Maestro
    path('Act_Maestro/', Act_Maestro.actividad_pagare_index, name='actividad_pagare_index'),
    path('Act_Maestro/crear/', Act_Maestro.actividad_pagare_crear, name='actividad_pagare_crear'),
    path('Act_Maestro/editar/<int:id>/', Act_Maestro.actividad_pagare_editar, name='actividad_pagare_editar'),
    path('Act_Maestro/eliminar/', Act_Maestro.actividad_pagare_eliminar, name='actividad_pagare_eliminar'),
    path('Act_Maestro/descargar_excel/', Act_Maestro.actividad_pagare_descargar_excel, name='actividad_pagare_descargar_excel'),


    # Rutas para tabla Certificacion
    path('certificacion/', Certificacion.certificacion_index, name='certificacion_index'),
    path('certificacion/crear', Certificacion.certificacion_crear, name='certificacion_crear'),
    path('certificacion/editar/<int:id>/', Certificacion.certificacion_editar, name='certificacion_editar'),
    path('certificacion/verificar-relaciones/', Certificacion.verificar_relaciones, name='verificar_relaciones'),
    path('certificacion/eliminar', Certificacion.certificacion_eliminar, name='certificacion_eliminar'),
    path('certificacion/descargar_excel', Certificacion.certificacion_descargar_excel, name='certificacion_descargar_excel'),
    
    # Rutas para tabla Costos Indirecto
    path('costos_indirectos/', CostosIndirectos.costos_indirectos_index, name='costos_indirectos_index'),
    path('costos_indirectos/crear', CostosIndirectos.costos_indirectos_crear, name='costos_indirectos_crear'),
    path('costos_indirectos/editar/<int:id>/', CostosIndirectos.costos_indirectos_editar, name='costos_indirectos_editar'),
    path('costos_indirectos/eliminar', CostosIndirectos.costos_indirectos_eliminar, name='costos_indirectos_eliminar'),
    path('costos_indirectos/verificar-relaciones/', CostosIndirectos.verificar_relaciones, name='costos_indirectos_verificar_relaciones'),
    path('costos_indirectos/descargar_excel', CostosIndirectos.costos_indirectos_descargar_excel, name='costos_indirectos_descargar_excel'),

    # Rutas para la tabla Concepto
    path('conceptos/', Conceptos.conceptos_index, name='conceptos_index'),
    path('conceptos/crear', Conceptos.conceptos_crear, name='conceptos_crear'),
    path('conceptos/editar/<int:id>/', Conceptos.conceptos_editar, name='conceptos_editar'),
    path('conceptos/eliminar', Conceptos.conceptos_eliminar, name='conceptos_eliminar'),
    path('conceptos/descargar_excel', Conceptos.conceptos_descargar_excel, name='conceptos_descargar_excel'),

    path('contactos/', contactos.contactos_index, name='contactos_index'),
    path('contactos/crear', contactos.contactos_crear, name='contactos_crear'),
    path('contactos/editar/<int:id>/', contactos.contactos_editar, name='contactos_editar'),
    path('contactos/eliminar', contactos.contactos_eliminar, name='contactos_eliminar'),
    path('contactos/descargar_excel', contactos.contactos_descargar_excel, name='contactos_descargar_excel'),

    # Rutas para tabla Clientes Contratos
    path('clientes_contratos/', clientes_Contratos.clientes_contratos_index, name='clientes_contratos_index'),
    path('clientes_contratos/crear', clientes_Contratos.clientes_contratos_crear, name='clientes_contratos_crear'),
    path('clientes_contratos/editar/<int:id>/', clientes_Contratos.clientes_contratos_editar, name='clientes_contratos_editar'),
    path('clientes_contratos/eliminar', clientes_Contratos.clientes_contratos_eliminar, name='clientes_contratos_eliminar'),
    path('clientes_contratos/descargar_excel', clientes_Contratos.clientes_contratos_descargar_excel, name='clientes_contratos_descargar_excel'),

    # Rutas para tabla Contratos Otros Si
    path('contratos_otros_si/', ContratosOtrosSi.contratos_otros_si_index, name='contratos_otros_si_index'),
    path('contratos_otros_si/crear', ContratosOtrosSi.contratos_otros_si_crear, name='contratos_otros_si_crear'),
    path('contratos_otros_si/editar/<int:id>/', ContratosOtrosSi.contratos_otros_si_editar, name='contratos_otros_si_editar'),
    path('contratos_otros_si/eliminar', ContratosOtrosSi.contratos_otros_si_eliminar, name='contratos_otros_si_eliminar'),
    path('contratos_otros_si/descargar_excel', ContratosOtrosSi.contratos_otros_si_descargar_excel, name='contratos_otros_si_descargar_excel'),
    path('contratos_otros_si/obtener-contratos/<int:cliente_id>/', ContratosOtrosSi.obtener_contratos_por_cliente, name='obtener_contratos_por_cliente'),

    # Rutas para Centros de Costos
    path('centros_costos/', centrosCostos.centros_costos_index, name='centros_costos_index'),
    path('centros_costos/crear', centrosCostos.centros_costos_crear, name='centros_costos_crear'),
    path('centros_costos/editar/<int:id>/', centrosCostos.centros_costos_editar, name='centros_costos_editar'),
    path('centros_costos/eliminar', centrosCostos.centros_costos_eliminar, name='centros_costos_eliminar'),
    path('centros_costos/verificar-relaciones/', centrosCostos.verificar_relaciones, name='centros_costos_verificar_relaciones'),
    path('centros_costos/descargar_excel', centrosCostos.centros_costos_descargar_excel, name='centros_costos_descargar_excel'),

    # Rutas para tabla Gastos
    path('gastos/', gastos.gasto_index, name='gastos_index'),
    path('gastos/crear', gastos.gasto_crear, name='gastos_crear'),
    path('gastos/editar/<int:id>/', gastos.gasto_editar, name='gastos_editar'),
    path('gastos/eliminar', gastos.gasto_eliminar, name='gastos_eliminar'),
    path('gastos/verificar-relaciones/', gastos.verificar_relaciones, name='gastos_verificar_relaciones'),
    path('gastos/descargar_excel', gastos.gasto_descargar_excel, name='gastos_descargar_excel'),

    # Rutas para tabla Detalle de Gastos
    path('detalle_gastos/', detalleGastos.detalle_gastos_index, name='detalle_gastos_index'),
    path('detalle_gastos/crear',detalleGastos.detalle_gastos_crear, name='detalle_gastos_crear'),
    path('detalle_gastos/editar/<int:id>/', detalleGastos.detalle_gastos_editar, name='detalle_gastos_editar'),
    path('detalle_gastos/eliminar', detalleGastos.detalle_gastos_eliminar, name='detalle_gastos_eliminar'),
    path('detalle_gastos/descargar_excel', detalleGastos.detalle_gastos_descargar_excel, name='detalle_gastos_descargar_excel'),

    # Rutas para tabla Total de Gastos
    path('total_gastos/', totalGasto.total_gastos_index, name='total_gastos_index'),
    path('total_gastos/crear', totalGasto.total_gastos_crear, name='total_gastos_crear'),
    path('total_gastos/detalles/editar/', totalGasto.editar_detalles_gastos, name='editar_detalles_gastos'),
    path('total_gastos/eliminar/', totalGasto.total_gastos_eliminar, name='total_gastos_eliminar'),
    path('total_gastos/visualizar/<int:id>/', totalGasto.visualizar_detalle_gastos, name='visualizar_detalle_gastos'),  # Nueva ruta para visualizar detalles
    path('total_gastos/descargar_excel', totalGasto.total_gastos_descargar_excel, name='total_gastos_descargar_excel'),
    path('total_gastos/<int:total_gastos_id>/agregar_detalle/', totalGasto.crear_detalle_gastos, name='crear_detalle_gastos'),
    path('total_gastos/actualizar_total/<int:anio>/<int:mes>/', totalGasto.actualizar_total, name='actualizar_total'),

    path('tipos_contactos/', tiposContactos.Tipos_contactos_index, name='tipos_contactos_index'),
    path('tipos_contactos/crear', tiposContactos.Tipos_contactos_crear, name='tipos_contactos_crear'),
    path('tipos_contactos/editar/<int:id>/', tiposContactos.Tipos_contactos_editar, name='tipos_contactos_editar'),
    path('tipos_contactos/verificar-relaciones/', tiposContactos.verificar_relaciones, name='verificar_relaciones'),
    path('tipos_contactos/eliminar', tiposContactos.Tipos_contactos_eliminar, name='tipos_contactos_eliminar'),
    path('tipos_contactos/descargar_excel', tiposContactos.Tipos_contactos_descargar_excel, name='tipos_contactos_descargar_excel'),

    # Rutas para tabla Total Costos Indirectos
    path('total_costos_indirectos/', totalCostos.total_costos_indirectos_index, name='total_costos_indirectos_index'),
    path('total_costos_indirectos/crear/', totalCostos.total_costos_indirectos_crear, name='total_costos_indirectos_crear'),
    path('total_costos_indirectos/eliminar/', totalCostos.total_costos_indirectos_eliminar, name='total_costos_indirectos_eliminar'),
    path('total_costos_indirectos/descargar_excel/', totalCostos.total_costos_indirectos_descargar_excel, name='total_costos_indirectos_descargar_excel'),
    path('total_costos_indirectos/visualizar/<int:id>/', totalCostos.visualizar_detalle_costos, name='visualizar_detalle_costos'),  # Nueva ruta para visualizar detalles
    path('total_costos_indirectos/detalles/editar/', totalCostos.editar_detalles_costos, name='editar_detalles_costos'),
    path('total_costos_indirectos/<int:total_costos_id>/agregar_detalle/', totalCostos.crear_detalle_costos, name='total_costos_crear_detalle'),
    path('total_costos_indirectos/actualizar_total/<int:anio>/<int:mes>/', totalCostos.actualizar_total, name='actualizar_total'),


    # Rutas para tabla Detalle Costos Indirectos
    path('detalle_costos_indirectos/', detallesCostosIndirectos.detalle_costos_indirectos_index, name='detalle_costos_indirectos_index'),
    path('detalle_costos_indirectos/crear', detallesCostosIndirectos.detalle_costos_indirectos_crear, name='detalle_costos_indirectos_crear'),
    path('detalle_costos_indirectos/editar/<int:id>/', detallesCostosIndirectos.detalle_costos_indirectos_editar, name='detalle_costos_indirectos_editar'),
    path('detalle_costos_indirectos/eliminar',detallesCostosIndirectos.detalle_costos_indirectos_eliminar, name='detalle_costos_indirectos_eliminar'),
    path('detalle_costos_indirectos/descargar_excel', detallesCostosIndirectos.detalle_costos_indirectos_descargar_excel, name='detalle_costos_indirectos_descargar_excel'),

    # Rutas para tabla Tarifa de Consultores
    path('tarifa_consultores/', tarifa_consultores.tarifa_consultores_index, name='tarifa_consultores_index'),
    path('tarifa_consultores/crear', tarifa_consultores.tarifa_consultores_crear, name='tarifa_consultores_crear'),
    path('tarifa_consultores/editar/<int:idd>/', tarifa_consultores.tarifa_consultores_editar, name='tarifa_consultores_editar'),
    path('tarifa_consultores/eliminar', tarifa_consultores.tarifa_consultores_eliminar, name='tarifa_consultores_eliminar'),
    path('tarifa_consultores/descargar_excel', tarifa_consultores.tarifa_consultores_descargar_excel, name='tarifa_consultores_descargar_excel'),

    # Rutas para tabla Tarifa de Clientes
    path('tarifa_clientes/', tarifa_Clientes.tarifa_clientes_index, name='tarifa_clientes_index'),
    path('tarifa_clientes/crear', tarifa_Clientes.tarifa_clientes_crear, name='tarifa_clientes_crear'),
    path('tarifa_clientes/editar/<int:id>/', tarifa_Clientes.tarifa_clientes_editar, name='tarifa_clientes_editar'),
    path('tarifa_clientes/eliminar', tarifa_Clientes.tarifa_clientes_eliminar, name='tarifa_clientes_eliminar'),
    path('tarifa_clientes/descargar_excel', tarifa_Clientes.tarifa_clientes_descargar_excel, name='tarifa_clientes_descargar_excel'),

    # Rutas para tabla Nomina
    path('nomina/', Nomina.nomina_index, name='nomina_index'),
    path('nomina/crear', Nomina.nomina_crear, name='nomina_crear'),
    path('nomina/editar/<str:id>/', Nomina.nomina_editar, name='nomina_editar'),
    path('nomina/eliminar', Nomina.nomina_eliminar, name='nomina_eliminar'),
    path('nomina/descargar_excel', Nomina.nomina_descargar_excel, name='nomina_descargar_excel'),

    # Rutas para tabla Detalle Certificación
    path('detalle_certificacion/', detallesCertificacion.detalle_certificacion_index, name='detalle_certificacion_index'),
    path('detalle_certificacion/crear/', detallesCertificacion.detalle_certificacion_crear, name='detalle_certificacion_crear'),
    path('detalle_certificacion/editar/<int:Id>/', detallesCertificacion.detalle_certificacion_editar, name='detalle_certificacion_editar'),
    path('detalle_certificacion/eliminar/', detallesCertificacion.detalle_certificacion_eliminar, name='detalle_certificacion_eliminar'),
    path('detalle_certificacion/descargar_excel/', detallesCertificacion.detalle_certificacion_descargar_excel, name='detalle_certificacion_descargar_excel'),

    # Rutas para la tabla Empleado
    path('empleado/', empleado.empleado_index, name='empleado_index'),
    path('empleado/crear/', empleado.empleado_crear, name='empleado_crear'),
    path('empleado/editar/<str:id>/', empleado.empleado_editar, name='empleado_editar'),
    path('empleado/eliminar/', empleado.empleado_eliminar, name='empleado_eliminar'),
    path('empleado/verificar-relaciones/', empleado.verificar_relaciones, name='empleado_verificar_relaciones'),
    path('empleado/descargar_excel/', empleado.empleado_descargar_excel, name='empleado_descargar_excel'),

    # Rutas para la tabla Horas Habiles
    path('horas_habiles/', Horas_Habiles.horas_habiles_index, name='horas_habiles_index'),
    path('horas_habiles/crear/', Horas_Habiles.horas_habiles_crear, name='horas_habiles_crear'),
    path('horas_habiles/editar/<str:id>/', Horas_Habiles.horas_habiles_editar, name='horas_habiles_editar'),
    path('horas_habiles/eliminar/', Horas_Habiles.horas_habiles_eliminar, name='horas_habiles_eliminar'),
    path('horas_habiles/verificar-relaciones/', Horas_Habiles.verificar_relaciones, name='Horas_Habiles_verificar_relaciones'),
    path('horas_habiles/descargar_excel/', Horas_Habiles.horas_habiles_descargar_excel, name='horas_habiles_descargar_excel'),


    # Rutas para tabla Empleados Estudios
    path('empleados_estudios/', empleados_estudios.empleados_estudios_index, name='empleados_estudios_index'),
    path('empleados_estudios/crear/', empleados_estudios.empleados_estudios_crear, name='empleados_estudios_crear'),
    path('empleados_estudios/editar/<int:id>/',empleados_estudios.empleados_estudios_editar, name='empleados_estudios_editar'),
    path('empleados_estudios/eliminar/', empleados_estudios.empleados_estudios_eliminar, name='empleados_estudios_eliminar'),
    path('empleados_estudios/descargar_excel/', empleados_estudios.empleados_estudios_descargarExcel, name='empleados_estudios_descargar_excel'),

    # Rutas para la tabla Registro Tiempos
    path('registro_tiempos/', registro_tiempos.registro_tiempos_index, name='registro_tiempos_index'),
    path('registro_tiempos/guardar/', registro_tiempos.registro_tiempos_guardar, name='registro_tiempos_guardar'),
    path('registro_tiempos/horas_habiles/', registro_tiempos.obtener_horas_habiles_view, name='obtener_horas_habiles'),

    # Rutas para informe de certificación
    path('informes/certificaciones/', Informe_certificaciones.empleado_filtrado, name='informes_certificacion_index'),
    path('informes/certificaciones/exportar_certificaciones_excel', Informe_certificaciones.exportar_certificaciones_excel, name='exportar_certificaciones_excel'),

    # Rutas para informe de salario
    path('informes/salarios/', empleado_nomina_filtrado.empleado_nomina_filtrado, name='informes_salarios_index'),
    path('informes/salarios/exportar_nomina_excel', empleado_nomina_filtrado.exportar_nomina_excel, name='exportar_nomina_excel'),
       
    # Rutas para informe de empleados
    path('informes/empleados/', informe_empleados.informe_empleados, name='informes_empleado_index'),
    path('informes/empleados/exportar_empleados_excel', informe_empleados.exportar_empleados_excel, name='exportar_empleados_excel'),

    #Ruta para informe de estudios
    path('informes/estudios/', informe_estudios.empleado_estudio_filtrado, name='informes_estudios_index'),
    path('informes/estudios/exportar_estudio_excel', informe_estudios.exportar_estudio_excel, name='exportar_estudio_excel'),

    #Ruta para informe de consultores
    path('informes/consultores/', informe_consultores.consultores_filtrado , name='informes_consultores_index'),
    path('informes/consultores/exportar_consultores_excel', informe_consultores.exportar_consultores_excel , name='exportar_consultores_excel'),

    #Ruta para informe de tarifas de consultores
    path('informes/tarifas_consultores/', informe_tarifas_consultores.tarifas_consultores_filtrado , name='informes_tarifas_consultores_index'),
    path('informes/tarifas_consultores/exportar_tarifas_consultores_excel', informe_tarifas_consultores.exportar_tarifas_consultores_excel , name='exportar_tarifas_consultores_excel'),

    #Ruta para informe de facturación
    path('informes/facturacion/', informe_facturacion.informes_facturacion_index , name='informes_facturacion_index'),
    path('informes/facturacion/descargar/', informe_facturacion.descargar_reporte_excel, name='descargar_reporte_excel'),

    #Ruta para informe de tarifas de clientes
    path('informes/tarifas_clientes/', informe_tarifas_clientes.tarifas_clientes_filtrado , name='informes_tarifas_clientes_index'),
    path('informes/tarifas_clientes/exportar_tarifas_clientes_excel', informe_tarifas_clientes.exportar_tarifas_clientes_excel , name='exportar_tarifas_clientes_excel'),

    #Ruta para informe de Clientes
    path('informes/informes_clientes/', Informe_clientes.clientes_filtrado, name='informes_clientes_index'),
    path('informes/informes_clientes/exportar_clientes_excel', Informe_clientes.exportar_clientes_excel , name='exportar_clientes_excel'),

    #Ruta para informe de Historial Cargos
    path('informes/informes_historial_cargos/', informe_historial_cargos.historial_cargos_filtrado, name='informes_historial_cargos_index'),
    path('informes/informes_historial_cargos/exportar_historial_cargos_excel', informe_historial_cargos.exportar_historial_cargos_excel , name='exportar_historial_cargos_excel'),

    #Ruta para informe clientes contratos
    path('informes/informes_clientes_contratos/', informe_clientes_contratos.clientes_contratos_filtrado, name='informes_clientes_contratos_index'),
    path('informes/informes_clientes_contratos/exportar_clientes_contratos_excel', informe_clientes_contratos.exportar_clientes_contratos_excel , name='exportar_clientes_contratos_excel'),

    # Ruta para informe de Otros Sí
    path('informes/informes_otros_si/', informe_otros_si.informe_otros_si, name='informes_otros_si_index'),
    path('informes/informes_otros_si/exportar_otros_si_excel', informe_otros_si.exportar_otros_si_excel, name='exportar_otros_si_excel'),
    path('api/get_cliente_id_by_nombre/', informe_otros_si.get_cliente_id_by_nombre, name='get_cliente_id_by_nombre'),
    path('contratos_otros_si/obtener-contratos/<int:cliente_id>/', ContratosOtrosSi.obtener_contratos_por_cliente, name='obtener_contratos_por_cliente'),
    

    #Ruta para informe tiempos consultores
    path('informes/tiempo_consultores/', informe_tiempos_consultores.tiempos_clientes_filtrado, name='informes_tiempos_consultores'),
    path("informes/tiempo_consultores/exportar_tiempo_consultores/",informe_tiempos_consultores.exportar_tiempos_clientes_excel, name="exportar_tiempos_clientes_excel"),

    # Rutas para tabla Historial Cargos
    path('historial_cargos/', historial_cargos.historial_cargos_index, name='historial_cargos_index'),
    path('historial_cargos/crear/', historial_cargos.historial_cargos_crear, name='historial_cargos_crear'),
    path('historial_cargos/editar/<int:id>/', historial_cargos.historial_cargos_editar, name='historial_cargos_editar'),
    path('historial_cargos/eliminar/', historial_cargos.historial_cargos_eliminar, name='historial_cargos_eliminar'),
    path('historial_cargos/descargar_excel/', historial_cargos.historial_cargos_descargar_excel, name='historial_cargos_descargar_excel'),

    # Rutas para la tabla Registro Tiempos
    path('clientes_factura/', clientes_factura.clientes_factura_index, name='clientes_factura_index'),
    path('clientes_factura/guardar/', clientes_factura.clientes_factura_guardar, name='clientes_factura_guardar'),
    path('clientes_factura/generar_plantilla/', clientes_factura.generar_plantilla, name='generar_plantilla'),
    path('clientes_factura/obtener_factura/', clientes_factura.obtener_tarifa, name='obtener_tarifa'),
    path('clientes_factura/get_lineas_modulos/', clientes_factura.get_lineas_modulos, name='get_lineas_modulos'),
    path('clientes_factura/eliminar/', clientes_factura.eliminar_facturas, name='eliminar_facturas'),

    # Rutas para la tabla Facturacion consultores
    path('facturacion_consultores/', facturacion_consultores.facturacion_consultores, name='facturacion_consultores_index'),
    path('facturacion_consultores/eliminar/', facturacion_consultores.eliminar_facturacion_consultores, name='eliminar_facturacion_consultores'),
    path('facturacion_consultores/guardar/', facturacion_consultores.guardar_facturacion_consultores, name='guardar_facturacion_consultores'),

    #Ruta para informe de Facturacion Consultores
    path('informes/informes_facturacion_consultores/', informe_facturacion_consultores.informe_totales_por_mes, name='informes_facturacion_consultores_index'),
    path('informes/informes_facturacion_consultores/reporte_excel_totales_por_mes', informe_facturacion_consultores.reporte_excel_totales_por_mes , name='reporte_excel_totales_por_mes'),

    #Ruta para informe de servicio Facturacion Consultores
    path('informes/informes_Serv_consultor/', informe_serv_consultor.informe_totales, name='informes_serv_consultor_index'),
    path('informes/informes_Serv_consultor/descargar_informe_totales_excel', informe_serv_consultor.descargar_reporte_excel_totales_por_mes, name='descargar_reporte_excel_totales_por_mes'),

    # Rutas para la tabla Indicadores de Operatividad
    path('indicadores_operatividad/', indicadores_operatividad.indicadores_operatividad_index, name='indicadores_operatividad_index'),

    # Rutas para la tabla Referencias
    path('referencia/', referencia.referencia_index, name='referencia_index'),
    path('referencia/crear', referencia.referencia_crear, name='referencia_crear'),
    path('referencia/editar/<int:id>/', referencia.referencia_editar, name='referencia_editar'),
    path('referencia/verificar-relaciones/', referencia.verificar_relaciones, name='verificar_relaciones'),
    path('referencia/eliminar', referencia.referencia_eliminar, name='referencia_eliminar'),
    path('referencia/descargar_excel', referencia.referencia_descargar_excel, name='referencia_descargar_excel'),

    # Rutas para la tabla Indicadores de totales
    path('indicadores_totales/', indicadores_totales.indicadores_totales, name='indicadores_totales_index'),
    path('indicadores_facturacion/', indicadores_facturacion.indicadores_facturacion, name='indicadores_facturacion_index'),
    path('indicadores_margen_cliente/', indicadores_margen_cliente.indicadores_margen_cliente, name='indicadores_margen_cliente_index'),

    #Ruta para la tabla Pagare
    path('Pagare/Pagare/', pagare_index, name="pagare_index"),
    path('pagare/<int:pagare_id>/planeado/', pag_planeado, name='pag_planeado'),
    path('guardar_pagare/', guardar_pagare, name='guardar_pagare'),
    path('pagare/<int:pagare_id>/ejecutado/', pag_ejecutado, name='pag_ejecutado'),
    path('obtener_pagares/', obtener_pagares_empleado, name='obtener_pagares'),
    path('pagare/eliminar/', eliminar_pagares, name='eliminar_pagares'),
    path('pagares/obtener_datos/', obtener_datos_pagares, name='obtener_datos_pagares'),
    path('pagares/actualizar/', actualizar_pagare, name='actualizar_pagare'),

    #Ruta de informes Pagare
    path('informes/pagares/', informe_pagares, name='informe_pagares'),
    path('informes/pagares/exportar_pagares_excel/', exportar_pagares_excel, name='exportar_pagares_excel'),

    #Ruta para informe de Facturacion Clientes
    path('informes/informes_facturacion_clientes/', informe_facturacion_clientes.informe_facturacion_clientes, name='informes_facturacion_clientes_index'),
    path('informes/informes_facturacion_clientes/descargar_informe_facturacion_clientes_excel/', informe_facturacion_clientes.descargar_reporte_excel_facturacion_clientes, name='descargar_reporte_excel_facturacion_clientes'),

    # URLs para TipoPagare
    path('TipoPagare/', tipo_pagare_index, name='tipo_pagare_index'),
    path('TipoPagare/crear/', tipo_pagare_crear, name='tipo_pagare_crear'),
    path('TipoPagare/editar/<int:id>/', tipo_pagare_editar, name='tipo_pagare_editar'),
    path('TipoPagare/eliminar/', tipo_pagare_eliminar, name='tipo_pagare_eliminar'),
    path('TipoPagare/confirmar_delete/<int:id>/', tipo_pagare_confirmar_delete, name='tipo_pagare_confirmar_delete'),
    path('TipoPagare/descargar_excel/', tipo_pagare_descargar_excel, name='tipo_pagare_descargar_excel'),
    ]

