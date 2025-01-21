from django.urls import path
from Modulo.Views import modulo
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
from Modulo.Views import empleado
from Modulo.Views import consultores
from Modulo.Views import Nomina
from Modulo.models import TiposContactos
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

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),

    # Rutas para tabla Modulo
    path('Modulo', modulo.modulo, name='Modulo'),
    path('Modulo/crear', modulo.crear, name='crear'),
    path('Modulo/editar/<int:id>/', modulo.editar, name='editar'),
    path('Modulo/eliminar', modulo.eliminar, name='eliminar'),
    path('verificar-relaciones/', modulo.verificar_relaciones, name='verificar_relaciones'),
    path('Modulo/descargar_excel', modulo.descargar_excel, name='descargar_excel'),

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
    path('verificar-relaciones/', TipoDocumento.verificar_relaciones, name='verificar_relaciones'),
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
    path('clientes/descargar_excel/', Clientes.clientes_descargar_excel, name='clientes_descargar_excel'),

    # Rutas para la tabla Consultores
    path('consultores/', consultores.consultores_index, name='consultores_index'),
    path('consultores/crear/', consultores.consultores_crear, name='consultores_crear'),
    path('consultores/editar/<str:id>/', consultores.consultores_editar, name='consultores_editar'),
    path('consultores/eliminar/', consultores.consultores_eliminar, name='consultores_eliminar'),
    path('consultores/verificar-relaciones/', consultores.verificar_relaciones, name='consultores_verificar_relaciones'),
    path('consultores/descargar_excel/', consultores.consultores_descargar_excel, name='consultores_descargar_excel'),

    # Rutas para tabla Certificacion
    path('certificacion/', Certificacion.certificacion_index, name='certificacion_index'),
    path('certificacion/crear', Certificacion.certificacion_crear, name='certificacion_crear'),
    path('certificacion/editar/<int:id>/', Certificacion.certificacion_editar, name='certificacion_editar'),
    path('certificacion/eliminar', Certificacion.certificacion_eliminar, name='certificacion_eliminar'),
    path('certificacion/descargar_excel', Certificacion.certificacion_descargar_excel, name='certificacion_descargar_excel'),
    
    # Rutas para tabla Costos Indirecto
    path('costos_indirectos/', CostosIndirectos.costos_indirectos_index, name='costos_indirectos_index'),
    path('costos_indirectos/crear', CostosIndirectos.costos_indirectos_crear, name='costos_indirectos_crear'),
    path('costos_indirectos/editar/<int:id>/', CostosIndirectos.costos_indirectos_editar, name='costos_indirectos_editar'),
    path('costos_indirectos/eliminar', CostosIndirectos.costos_indirectos_eliminar, name='costos_indirectos_eliminar'),
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
    path('total_gastos/editar/<int:id>/', totalGasto.total_gastos_editar, name='total_gastos_editar'),
    path('total_gastos/eliminar', totalGasto.total_gastos_eliminar, name='total_gastos_eliminar'),
    path('total_gastos/descargar_excel', totalGasto.total_gastos_descargar_excel, name='total_gastos_descargar_excel'),

    path('tipos_contactos/', tiposContactos.Tipos_contactos_index, name='tipos_contactos_index'),
    path('tipos_contactos/crear', tiposContactos.Tipos_contactos_crear, name='tipos_contactos_crear'),
    path('tipos_contactos/editar/<int:id>/', tiposContactos.Tipos_contactos_editar, name='tipos_contactos_editar'),
    path('tipos_contactos/verificar-relaciones/', tiposContactos.verificar_relaciones, name='verificar_relaciones'),
    path('tipos_contactos/eliminar', tiposContactos.Tipos_contactos_eliminar, name='tipos_contactos_eliminar'),
    path('tipos_contactos/descargar_excel', tiposContactos.Tipos_contactos_descargar_excel, name='tipos_contactos_descargar_excel'),

    # Rutas para tabla Total Costos Indirectos
    path('total_costos_indirectos/', totalCostos.total_costos_indirectos_index, name='total_costos_indirectos_index'),
    path('total_costos_indirectos/crear/', totalCostos.total_costos_indirectos_crear, name='total_costos_indirectos_crear'),
    path('total_costos_indirectos/editar/<int:id>/', totalCostos.total_costos_indirectos_editar, name='total_costos_indirectos_editar'),
    path('total_costos_indirectos/eliminar/', totalCostos.total_costos_indirectos_eliminar, name='total_costos_indirectos_eliminar'),
    path('total_costos_indirectos/descargar_excel/', totalCostos.total_costos_indirectos_descargar_excel, name='total_costos_indirectos_descargar_excel'),

    # Rutas para tabla Detalle Costos Indirectos
    path('detalle_costos_indirectos/', detallesCostosIndirectos.detalle_costos_indirectos_index, name='detalle_costos_indirectos_index'),
    path('detalle_costos_indirectos/crear', detallesCostosIndirectos.detalle_costos_indirectos_crear, name='detalle_costos_indirectos_crear'),
    path('detalle_costos_indirectos/editar/<int:id>/', detallesCostosIndirectos.detalle_costos_indirectos_editar, name='detalle_costos_indirectos_editar'),
    path('detalle_costos_indirectos/eliminar',detallesCostosIndirectos.detalle_costos_indirectos_eliminar, name='detalle_costos_indirectos_eliminar'),
    path('detalle_costos_indirectos/descargar_excel', detallesCostosIndirectos.detalle_costos_indirectos_descargar_excel, name='detalle_costos_indirectos_descargar_excel'),

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
    path('informes/', views.empleado_filtrado, name='informes_certificacion_index'),
    path('descargar_excel/', modulo.descargar_excel, name='descargar_excel'),

    # Rutas para informe de salario
    path('informes/salarios/', empleado_nomina_filtrado.empleado_nomina_filtrado, name='informes_salarios_index'),
    path('informes/salarios/exportar_nomina_excel', empleado_nomina_filtrado.exportar_nomina_excel, name='exportar_nomina_excel'),
       
    # Rutas para informe de empleados
    path('informes/empleados/', informe_empleados.informe_empleados, name='informes_empleado_index'),
    path('informes/empleados/exportar_empleados_excel', informe_empleados.exportar_empleados_excel, name='exportar_empleados_excel'),

    # Rutas para tabla Historial Cargos
    path('historial_cargos/', historial_cargos.historial_cargos_index, name='historial_cargos_index'),
    path('historial_cargos/crear/', historial_cargos.historial_cargos_crear, name='historial_cargos_crear'),
    path('historial_cargos/editar/<int:id>/', historial_cargos.historial_cargos_editar, name='historial_cargos_editar'),
    path('historial_cargos/eliminar/', historial_cargos.historial_cargos_eliminar, name='historial_cargos_eliminar'),
    path('historial_cargos/descargar_excel/', historial_cargos.historial_cargos_descargar_excel, name='historial_cargos_descargar_excel'),

]
