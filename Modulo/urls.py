from django.urls import path
from Modulo.Views import ActMaestro, InformeClientes, ClientesFactura, IndicadoresOperatividad, IndicadoresTotales, InformeFacturacionCentrocostos, InformeTiemposConsultores, Modulo
from Modulo.Views import Ipc
from Modulo.Views import Ind
from Modulo.Views import TipoDocumento
from Modulo.Views import Certificacion
from Modulo.Views import Conceptos
from Modulo.Views import Clientes
from Modulo.Views import CostosIndirectos
from Modulo.Views import Gastos
from Modulo.Views import Cargos
from Modulo.Views import EmpleadoNominaFiltrado
from Modulo.Views import InformeEmpleados
from Modulo.Views import InformeEstudios  
from Modulo.Views import InformeConsultores
from Modulo.Views import InformeTarifasConsultores
from Modulo.Views import InformeTarifasClientes
from Modulo.Views import InformeClientesContratos
from Modulo.Views import InformeOtrosSi
from Modulo.Views import Empleado
from Modulo.Views import Consultores
from Modulo.Views import Nomina
from Modulo.Views.Nomina import (
    nomina_index, nomina_crear, nomina_editar, nomina_eliminar,
    nomina_descargar_excel, verificar_relaciones,
    nomina_bulk_preview, nomina_bulk_create,   # <-- NUEVO
)
from Modulo.Views import InformeCertificaciones
from Modulo.Views.InformePagare import exportar_pagares_excel, informe_pagares
from Modulo.Views.Pagare import actualizar_pagare, eliminar_pagares, guardar_pagare, obtener_datos_pagares, obtener_pagares_empleado, pag_ejecutado, pag_planeado, pagare_index
from Modulo.Views.TipoPagare import tipo_pagare_confirmar_delete, tipo_pagare_crear, tipo_pagare_descargar_excel, tipo_pagare_editar, tipo_pagare_eliminar, tipo_pagare_index
from Modulo.models import TiposContactos
from Modulo.views import ActividadPagare
from . import views
from Modulo.Views import Perfil
from Modulo.Views import Linea
from Modulo.Views import DetallesCostosIndirectos
from Modulo.Views import DetallesCertificacion
from Modulo.Views import DetalleGastos
from Modulo.Views import TotalGasto
from Modulo.Views import TotalCostos
from Modulo.Views import TiposContactos
from Modulo.Views import Contactos
from Modulo.Views import HistorialCargos
from Modulo.Views import EmpleadosEstudios
from Modulo.Views import RegistroTiempos
from Modulo.Views import HorasHabiles
from Modulo.Views import TarifaConsultores
from Modulo.Views import Moneda
from Modulo.Views import ClientesContratos
from Modulo.Views import ContratosOtrosSi
from Modulo.Views import TarifaClientes
from Modulo.Views import Referencia
from Modulo.Views import CentrosCostos
from Modulo.Views import InformeFacturacion
from Modulo.Views import InformeHistorialCargos
from Modulo.Views import IndicadoresFacturacion
from Modulo.Views import IndicadoresMargenCliente
from Modulo.Views import LineaClienteCentrocostos
from Modulo.Views import FacturacionConsultores
from Modulo.Views import InformeFacturacionConsultores
from Modulo.Views import InformeServConsultor
from Modulo.Views import AuthViews
from Modulo.Views import InformeDetalleFacturacionConsultores



urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.inicio, name='inicio'),
    path('nosotros', views.nosotros, name='nosotros'),

    # Rutas para tabla Modulo
    path('Modulo', Modulo.modulo, name='Modulo'),
    path('Modulo/crear', Modulo.crear, name='crear'),
    path('Modulo/editar/<int:id>/', Modulo.editar, name='editar'),
    path('Modulo/eliminar', Modulo.eliminar, name='eliminar'),
    path('verificar-relaciones/', Modulo.verificar_relaciones, name='verificar_relaciones'),
    path('Modulo/descargar_excel', Modulo.descargar_excel, name='descargar_excel'),

    # Rutas para tabla Moneda
    path('moneda/', Moneda.moneda_index, name='moneda_index'),
    path('moneda/crear', Moneda.moneda_crear, name='moneda_crear'),
    path('moneda/editar/<int:id>/', Moneda.moneda_editar, name='moneda_editar'),
    path('moneda/eliminar', Moneda.moneda_eliminar, name='moneda_eliminar'),
    path('moneda/verificar-relaciones/', Moneda.verificar_relaciones, name='verificar_relaciones'),
    path('moneda/descargar_excel', Moneda.moneda_descargar_excel, name='moneda_descargar_excel'),

    # Rutas para la tabla IPC
    path('ipc/', Ipc.ipc_index, name='ipc_index'),
    path('ipc/crear', Ipc.ipc_crear, name='ipc_crear'),
    path('ipc/editar/<int:id>/', Ipc.ipc_editar, name='ipc_editar'),
    path('ipc/eliminar', Ipc.ipc_eliminar, name='ipc_eliminar'),
    path('ipc/descargar_excel', Ipc.ipc_descargar_excel, name='ipc_descargar_excel'),

    # Rutas para tabla IND
    path('ind/', Ind.ind_index, name='ind_index'),
    path('ind/crear', Ind.ind_crear, name='ind_crear'),
    path('ind/editar/<int:id>/', Ind.ind_editar, name='ind_editar'),
    path('ind/eliminar', Ind.ind_eliminar, name='ind_eliminar'),
    path('ind/descargar_excel', Ind.ind_descargar_excel, name='ind_descargar_excel'),

    # Rutas para tabla Línea
    path('linea/', Linea.linea_index, name='linea_index'),
    path('linea/crear', Linea.linea_crear, name='linea_crear'),
    path('linea/editar/<int:id>/', Linea.linea_editar, name='linea_editar'),
    path('linea/verificar-relaciones/', Linea.verificar_relaciones, name='verificar_relaciones'),
    path('linea/eliminar', Linea.linea_eliminar, name='linea_eliminar'),
    path('linea/descargar_excel', Linea.linea_descargar_excel, name='linea_descargar_excel'),

    # Rutas para tabla Perfil
    path('perfil/', Perfil.perfil_index, name='perfil_index'),
    path('perfil/crear', Perfil.perfil_crear, name='perfil_crear'),
    path('perfil/editar/<int:id>/', Perfil.perfil_editar, name='perfil_editar'),
    path('verificar-relaciones/', Perfil.verificar_relaciones, name='verificar_relaciones'),
    path('perfil/eliminar', Perfil.perfil_eliminar, name='perfil_eliminar'),
    path('perfil/descargar_excel', Perfil.perfil_descargar_excel, name='perfil_descargar_excel'),

     # Rutas para tabla TipoDocumento
    path('tipo_documento/', TipoDocumento.tipo_documento_index, name='tipo_documento_index'),
    path('tipo_documento/crear', TipoDocumento.tipo_documento_crear, name='tipo_documento_crear'),
    path('tipo_documento/editar/<int:id>/', TipoDocumento.tipo_documento_editar, name='tipo_documento_editar'),
    path('tipo_documento/verificar-relaciones/', TipoDocumento.verificar_relaciones, name='verificar_relaciones'),
    path('tipo_documento/eliminar', TipoDocumento.tipo_documento_eliminar, name='tipo_documento_eliminar'),
    path('tipo_documento/descargar_excel', TipoDocumento.tipo_documento_descargar_excel, name='tipo_documento_descargar_excel'),

    # Rutas para tabla Modulo
    path('Cargos/', Cargos.cargos_index, name='cargos_index'),
    path('Cargos/crear', Cargos.crear, name='cargos_crear'),
    path('Cargos/editar/<int:id>/', Cargos.editar, name='cargos_editar'),
    path('Cargos/eliminar', Cargos.eliminar, name='cargos_eliminar'),
    path('Cargos/verificar-relaciones/', Cargos.verificar_relaciones, name='cargos_verificar_relaciones'),
    path('Cargos/descargar_excel', Cargos.descargar_excel, name='cargos_descargar_excel'),

    # Rutas para la tabla Clientes
    path('clientes/', Clientes.clientes_index, name='clientes_index'),
    path('clientes/crear/', Clientes.clientes_crear, name='clientes_crear'),
    path('clientes/editar/<int:id>/', Clientes.clientes_editar, name='clientes_editar'),
    path('clientes/eliminar/', Clientes.clientes_eliminar, name='clientes_eliminar'),
    path('clientes/verificar-relaciones/', Clientes.verificar_relaciones, name='clientes_verificar_relaciones'),
    path('clientes/descargar_excel/', Clientes.clientes_descargar_excel, name='clientes_descargar_excel'),
    path('clientes/contactos/', Clientes.obtener_contactos, name='obtener_contactos'),# Nueva ruta para obtener contactos

    # Rutas para la tabla Consultores
    path('consultores/', Consultores.consultores_index, name='consultores_index'),
    path('consultores/crear/', Consultores.consultores_crear, name='consultores_crear'),
    path('consultores/editar/<str:id>/', Consultores.consultores_editar, name='consultores_editar'),
    path('consultores/eliminar/', Consultores.consultores_eliminar, name='consultores_eliminar'),
    path('consultores/verificar-relaciones/', Consultores.verificar_relaciones, name='consultores_verificar_relaciones'),
    path('consultores/descargar_excel/', Consultores.consultores_descargar_excel, name='consultores_descargar_excel'),

    #Ruta para tabla Actividades Maestro
    path('Act_Maestro/', ActMaestro.actividad_pagare_index, name='actividad_pagare_index'),
    path('Act_Maestro/crear/', ActMaestro.actividad_pagare_crear, name='actividad_pagare_crear'),
    path('Act_Maestro/editar/<int:id>/', ActMaestro.actividad_pagare_editar, name='actividad_pagare_editar'),
    path('Act_Maestro/eliminar/', ActMaestro.actividad_pagare_eliminar, name='actividad_pagare_eliminar'),
    path('Act_Maestro/descargar_excel/', ActMaestro.actividad_pagare_descargar_excel, name='actividad_pagare_descargar_excel'),


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

    path('contactos/', Contactos.contactos_index, name='contactos_index'),
    path('contactos/crear', Contactos.contactos_crear, name='contactos_crear'),
    path('contactos/editar/<int:id>/', Contactos.contactos_editar, name='contactos_editar'),
    path('contactos/eliminar', Contactos.contactos_eliminar, name='contactos_eliminar'),
    path('contactos/descargar_excel', Contactos.contactos_descargar_excel, name='contactos_descargar_excel'),

    # Rutas para tabla Clientes Contratos
    path('clientes_contratos/', ClientesContratos.clientes_contratos_index, name='clientes_contratos_index'),
    path('clientes_contratos/crear', ClientesContratos.clientes_contratos_crear, name='clientes_contratos_crear'),
    path('clientes_contratos/editar/<int:id>/', ClientesContratos.clientes_contratos_editar, name='clientes_contratos_editar'),
    path('clientes_contratos/eliminar', ClientesContratos.clientes_contratos_eliminar, name='clientes_contratos_eliminar'),
    path('clientes_contratos/descargar_excel', ClientesContratos.clientes_contratos_descargar_excel, name='clientes_contratos_descargar_excel'),

    # Rutas para tabla Contratos Otros Si
    path('contratos_otros_si/', ContratosOtrosSi.contratos_otros_si_index, name='contratos_otros_si_index'),
    path('contratos_otros_si/crear', ContratosOtrosSi.contratos_otros_si_crear, name='contratos_otros_si_crear'),
    path('contratos_otros_si/editar/<int:id>/', ContratosOtrosSi.contratos_otros_si_editar, name='contratos_otros_si_editar'),
    path('contratos_otros_si/eliminar', ContratosOtrosSi.contratos_otros_si_eliminar, name='contratos_otros_si_eliminar'),
    path('contratos_otros_si/descargar_excel', ContratosOtrosSi.contratos_otros_si_descargar_excel, name='contratos_otros_si_descargar_excel'),
    path('contratos_otros_si/obtener-contratos/<int:cliente_id>/', ContratosOtrosSi.obtener_contratos_por_cliente, name='obtener_contratos_por_cliente'),

    # Rutas para Centros de Costos
    path('centros_costos/', CentrosCostos.centros_costos_index, name='centros_costos_index'),
    path('centros_costos/crear', CentrosCostos.centros_costos_crear, name='centros_costos_crear'),
    path('centros_costos/editar/<int:id>/', CentrosCostos.centros_costos_editar, name='centros_costos_editar'),
    path('centros_costos/eliminar', CentrosCostos.centros_costos_eliminar, name='centros_costos_eliminar'),
    path('centros_costos/verificar-relaciones/', CentrosCostos.verificar_relaciones, name='centros_costos_verificar_relaciones'),
    path('centros_costos/descargar_excel', CentrosCostos.centros_costos_descargar_excel, name='centros_costos_descargar_excel'),

    # Rutas para tabla Gastos
    path('gastos/', Gastos.gasto_index, name='gastos_index'),
    path('gastos/crear', Gastos.gasto_crear, name='gastos_crear'),
    path('gastos/editar/<int:id>/', Gastos.gasto_editar, name='gastos_editar'),
    path('gastos/eliminar', Gastos.gasto_eliminar, name='gastos_eliminar'),
    path('gastos/verificar-relaciones/', Gastos.verificar_relaciones, name='gastos_verificar_relaciones'),
    path('gastos/descargar_excel', Gastos.gasto_descargar_excel, name='gastos_descargar_excel'),

    # Rutas para tabla Detalle de Gastos
    path('detalle_gastos/', DetalleGastos.detalle_gastos_index, name='detalle_gastos_index'),
    path('detalle_gastos/crear',DetalleGastos.detalle_gastos_crear, name='detalle_gastos_crear'),
    path('detalle_gastos/editar/<int:id>/', DetalleGastos.detalle_gastos_editar, name='detalle_gastos_editar'),
    path('detalle_gastos/eliminar', DetalleGastos.detalle_gastos_eliminar, name='detalle_gastos_eliminar'),
    path('detalle_gastos/descargar_excel', DetalleGastos.detalle_gastos_descargar_excel, name='detalle_gastos_descargar_excel'),

    # Rutas para tabla Total de Gastos
    path('total_gastos/', TotalGasto.total_gastos_index, name='total_gastos_index'),
    path('total_gastos/crear', TotalGasto.total_gastos_crear, name='total_gastos_crear'),
    path('total_gastos_editar/', TotalGasto.total_gastos_editar, name='total_gastos_editar'),
    path('total_gastos/eliminar/', TotalGasto.total_gastos_eliminar, name='total_gastos_eliminar'),
    path('total_gastos/visualizar/<int:id>/', TotalGasto.visualizar_detalle_gastos, name='visualizar_detalle_gastos'),  # Nueva ruta para visualizar detalles
    path('total_gastos/descargar_excel', TotalGasto.total_gastos_descargar_excel, name='total_gastos_descargar_excel'),
    path('total_gastos/<int:total_gastos_id>/agregar_detalle/', TotalGasto.crear_detalle_gastos, name='crear_detalle_gastos'),
    path('total_gastos/actualizar_total/<int:anio>/<int:mes>/', TotalGasto.actualizar_total, name='actualizar_total'),

    path('tipos_contactos/', TiposContactos.Tipos_contactos_index, name='tipos_contactos_index'),
    path('tipos_contactos/crear', TiposContactos.Tipos_contactos_crear, name='tipos_contactos_crear'),
    path('tipos_contactos/editar/<int:id>/', TiposContactos.Tipos_contactos_editar, name='tipos_contactos_editar'),
    path('tipos_contactos/verificar-relaciones/', TiposContactos.verificar_relaciones, name='verificar_relaciones'),
    path('tipos_contactos/eliminar', TiposContactos.Tipos_contactos_eliminar, name='tipos_contactos_eliminar'),
    path('tipos_contactos/descargar_excel', TiposContactos.Tipos_contactos_descargar_excel, name='tipos_contactos_descargar_excel'),

    # Rutas para tabla Total Costos Indirectos
    path('total_costos_indirectos/', TotalCostos.total_costos_indirectos_index, name='total_costos_indirectos_index'),
    path('total_costos_indirectos/crear/', TotalCostos.total_costos_indirectos_crear, name='total_costos_indirectos_crear'),
    path('total_costos_indirectos/editar/', TotalCostos.total_costos_indirectos_editar, name='total_costos_indirectos_editar'),
    path('total_costos_indirectos/eliminar/', TotalCostos.total_costos_indirectos_eliminar, name='total_costos_indirectos_eliminar'),
    path('total_costos_indirectos/descargar_excel/', TotalCostos.total_costos_indirectos_descargar_excel, name='total_costos_indirectos_descargar_excel'),
    path('total_costos_indirectos/visualizar/<int:id>/', TotalCostos.visualizar_detalle_costos, name='visualizar_detalle_costos'),  # Nueva ruta para visualizar detalles
    path('total_costos_indirectos/detalles/editar/', TotalCostos.editar_detalles_costos, name='editar_detalles_costos'),
    path('total_costos_indirectos/<int:total_costos_id>/agregar_detalle/', TotalCostos.crear_detalle_costos, name='total_costos_crear_detalle'),
    path('total_costos_indirectos/actualizar_total/<int:anio>/<int:mes>/', TotalCostos.actualizar_total, name='actualizar_total'),


    # Rutas para tabla Detalle Costos Indirectos
    path('detalle_costos_indirectos/', DetallesCostosIndirectos.detalle_costos_indirectos_index, name='detalle_costos_indirectos_index'),
    path('detalle_costos_indirectos/crear', DetallesCostosIndirectos.detalle_costos_indirectos_crear, name='detalle_costos_indirectos_crear'),
    path('detalle_costos_indirectos/editar/<int:id>/', DetallesCostosIndirectos.detalle_costos_indirectos_editar, name='detalle_costos_indirectos_editar'),
    path('detalle_costos_indirectos/eliminar',DetallesCostosIndirectos.detalle_costos_indirectos_eliminar, name='detalle_costos_indirectos_eliminar'),
    path('detalle_costos_indirectos/descargar_excel', DetallesCostosIndirectos.detalle_costos_indirectos_descargar_excel, name='detalle_costos_indirectos_descargar_excel'),

    # Rutas para tabla Tarifa de Consultores
    path('tarifa_consultores/', TarifaConsultores.tarifa_consultores_index, name='tarifa_consultores_index'),
    path('tarifa_consultores/crear', TarifaConsultores.tarifa_consultores_crear, name='tarifa_consultores_crear'),
    path('tarifa_consultores/editar/<int:idd>/', TarifaConsultores.tarifa_consultores_editar, name='tarifa_consultores_editar'),
    path('tarifa_consultores/eliminar', TarifaConsultores.tarifa_consultores_eliminar, name='tarifa_consultores_eliminar'),
    path('tarifa_consultores/descargar_excel', TarifaConsultores.tarifa_consultores_descargar_excel, name='tarifa_consultores_descargar_excel'),

    # Rutas para tabla Tarifa de Clientes
    path('tarifa_clientes/', TarifaClientes.tarifa_clientes_index, name='tarifa_clientes_index'),
    path('tarifa_clientes/crear', TarifaClientes.tarifa_clientes_crear, name='tarifa_clientes_crear'),
    path('tarifa_clientes/editar/<int:id>/', TarifaClientes.tarifa_clientes_editar, name='tarifa_clientes_editar'),
    path('tarifa_clientes/eliminar', TarifaClientes.tarifa_clientes_eliminar, name='tarifa_clientes_eliminar'),
    path('tarifa_clientes/descargar_excel', TarifaClientes.tarifa_clientes_descargar_excel, name='tarifa_clientes_descargar_excel'),

    # Rutas para tabla Nomina
    path('nomina/', Nomina.nomina_index, name='nomina_index'),
    path('nomina/crear', Nomina.nomina_crear, name='nomina_crear'),
    path('nomina/editar/<str:id>/', Nomina.nomina_editar, name='nomina_editar'),
    path('nomina/eliminar', Nomina.nomina_eliminar, name='nomina_eliminar'),
    path('nomina/descargar_excel', Nomina.nomina_descargar_excel, name='nomina_descargar_excel'),
    path('nomina/verificar-relaciones/', Nomina.verificar_relaciones, name='nomina_verificar_relaciones'),

    # Guardado masivo  
    path('nomina/bulk/preview/', nomina_bulk_preview, name='nomina_bulk_preview'),
    path('nomina/bulk/create/', nomina_bulk_create, name='nomina_bulk_create'),


    # Rutas para tabla Detalle Certificación
    path('detalle_certificacion/', DetallesCertificacion.detalle_certificacion_index, name='detalle_certificacion_index'),
    path('detalle_certificacion/crear/', DetallesCertificacion.detalle_certificacion_crear, name='detalle_certificacion_crear'),
    path('detalle_certificacion/editar/<int:Id>/', DetallesCertificacion.detalle_certificacion_editar, name='detalle_certificacion_editar'),
    path('detalle_certificacion/eliminar/', DetallesCertificacion.detalle_certificacion_eliminar, name='detalle_certificacion_eliminar'),
    path('detalle_certificacion/descargar_excel/', DetallesCertificacion.detalle_certificacion_descargar_excel, name='detalle_certificacion_descargar_excel'),

    # Rutas para la tabla Empleado
    path('empleado/', Empleado.empleado_index, name='empleado_index'),
    path('empleado/crear/', Empleado.empleado_crear, name='empleado_crear'),
    path('empleado/editar/<str:id>/', Empleado.empleado_editar, name='empleado_editar'),
    path('empleado/eliminar/', Empleado.empleado_eliminar, name='empleado_eliminar'),
    path('empleado/verificar-relaciones/', Empleado.verificar_relaciones, name='empleado_verificar_relaciones'),
    path('empleado/descargar_excel/', Empleado.empleado_descargar_excel, name='empleado_descargar_excel'),

    # Rutas para la tabla Horas Habiles
    path('horas_habiles/', HorasHabiles.horas_habiles_index, name='horas_habiles_index'),
    path('horas_habiles/crear/', HorasHabiles.horas_habiles_crear, name='horas_habiles_crear'),
    path('horas_habiles/editar/<str:id>/', HorasHabiles.horas_habiles_editar, name='horas_habiles_editar'),
    path('horas_habiles/eliminar/', HorasHabiles.horas_habiles_eliminar, name='horas_habiles_eliminar'),
    path('horas_habiles/verificar-relaciones/', HorasHabiles.verificar_relaciones, name='Horas_Habiles_verificar_relaciones'),
    path('horas_habiles/descargar_excel/', HorasHabiles.horas_habiles_descargar_excel, name='horas_habiles_descargar_excel'),


    # Rutas para tabla Empleados Estudios
    path('empleados_estudios/', EmpleadosEstudios.empleados_estudios_index, name='empleados_estudios_index'),
    path('empleados_estudios/crear/', EmpleadosEstudios.empleados_estudios_crear, name='empleados_estudios_crear'),
    path('empleados_estudios/editar/<int:id>/',EmpleadosEstudios.empleados_estudios_editar, name='empleados_estudios_editar'),
    path('empleados_estudios/eliminar/', EmpleadosEstudios.empleados_estudios_eliminar, name='empleados_estudios_eliminar'),
    path('empleados_estudios/descargar_excel/', EmpleadosEstudios.empleados_estudios_descargarExcel, name='empleados_estudios_descargar_excel'),

    # Rutas para la tabla Registro Tiempos
    path('registro_tiempos/', RegistroTiempos.registro_tiempos_index, name='registro_tiempos_index'),
    path('registro_tiempos/guardar/', RegistroTiempos.registro_tiempos_guardar, name='registro_tiempos_guardar'),
    path('registro_tiempos/horas_habiles/', RegistroTiempos.obtener_horas_habiles_view, name='obtener_horas_habiles'),

    # Rutas para informe de certificación
    path('Informes/certificaciones/', InformeCertificaciones.empleado_filtrado, name='informes_certificacion_index'),
    path('Informes/certificaciones/exportar_certificaciones_excel', InformeCertificaciones.exportar_certificaciones_excel, name='exportar_certificaciones_excel'),

    # Rutas para informe de salario
    path('Informes/salarios/', EmpleadoNominaFiltrado.empleado_nomina_filtrado, name='informes_salarios_index'),
    path('Informes/salarios/exportar_nomina_excel', EmpleadoNominaFiltrado.exportar_nomina_excel, name='exportar_nomina_excel'),
       
    # Rutas para informe de empleados
    path('Informes/empleados/', InformeEmpleados.informe_empleados, name='informes_empleado_index'),
    path('Informes/empleados/exportar_empleados_excel', InformeEmpleados.exportar_empleados_excel, name='exportar_empleados_excel'),

    #Ruta para informe de estudios
    path('Informes/estudios/', InformeEstudios.empleado_estudio_filtrado, name='informes_estudios_index'),
    path('Informes/estudios/exportar_estudio_excel', InformeEstudios.exportar_estudio_excel, name='exportar_estudio_excel'),

    #Ruta para informe de consultores
    path('Informes/consultores/', InformeConsultores.consultores_filtrado , name='informes_consultores_index'),
    path('Informes/consultores/exportar_consultores_excel', InformeConsultores.exportar_consultores_excel , name='exportar_consultores_excel'),

    #Ruta para informe de tarifas de consultores
    path('Informes/tarifas_consultores/', InformeTarifasConsultores.tarifas_consultores_filtrado , name='informes_tarifas_consultores_index'),
    path('Informes/tarifas_consultores/exportar_tarifas_consultores_excel', InformeTarifasConsultores.exportar_tarifas_consultores_excel , name='exportar_tarifas_consultores_excel'),

    #Ruta para informe de facturación
    path('Informes/facturacion/', InformeFacturacion.informes_facturacion_index , name='informes_facturacion_index'),
    path('Informes/facturacion/descargar/', InformeFacturacion.descargar_reporte_excel, name='descargar_reporte_excel'),

    #Ruta para informe de tarifas de clientes
    path('Informes/tarifas_clientes/', InformeTarifasClientes.tarifas_clientes_filtrado , name='informes_tarifas_clientes_index'),
    path('Informes/tarifas_clientes/exportar_tarifas_clientes_excel', InformeTarifasClientes.exportar_tarifas_clientes_excel , name='exportar_tarifas_clientes_excel'),

    #Ruta para informe de Clientes
    path('Informes/informes_clientes/', InformeClientes.clientes_filtrado, name='informes_clientes_index'),
    path('Informes/informes_clientes/exportar_clientes_excel', InformeClientes.exportar_clientes_excel , name='exportar_clientes_excel'),

    #Ruta para informe de Historial Cargos
    path('Informes/informes_historial_cargos/', InformeHistorialCargos.historial_cargos_filtrado, name='informes_historial_cargos_index'),
    path('Informes/informes_historial_cargos/exportar_historial_cargos_excel', InformeHistorialCargos.exportar_historial_cargos_excel , name='exportar_historial_cargos_excel'),

    #Ruta para informe clientes contratos
    path('Informes/informes_clientes_contratos/', InformeClientesContratos.clientes_contratos_filtrado, name='informes_clientes_contratos_index'),
    path('Informes/informes_clientes_contratos/exportar_clientes_contratos_excel', InformeClientesContratos.exportar_clientes_contratos_excel , name='exportar_clientes_contratos_excel'),

    # Ruta para informe de Otros Sí
    path('Informes/informes_otros_si/', InformeOtrosSi.informe_otros_si, name='informes_otros_si_index'),
    path('Informes/informes_otros_si/exportar_otros_si_excel', InformeOtrosSi.exportar_otros_si_excel, name='exportar_otros_si_excel'),
    path('api/get_cliente_id_by_nombre/', InformeOtrosSi.get_cliente_id_by_nombre, name='get_cliente_id_by_nombre'),
    path('contratos_otros_si/obtener-contratos/<int:cliente_id>/', ContratosOtrosSi.obtener_contratos_por_cliente, name='obtener_contratos_por_cliente'),
    

    #Ruta para informe tiempos consultores
    path('Informes/tiempo_consultores/', InformeTiemposConsultores.tiempos_clientes_filtrado, name='informes_tiempos_consultores'),
    path("Informes/tiempo_consultores/exportar_tiempo_consultores/",InformeTiemposConsultores.exportar_tiempos_clientes_excel, name="exportar_tiempos_clientes_excel"),

    # Rutas para tabla Historial Cargos
    path('historial_cargos/', HistorialCargos.historial_cargos_index, name='historial_cargos_index'),
    path('historial_cargos/crear/', HistorialCargos.historial_cargos_crear, name='historial_cargos_crear'),
    path('historial_cargos/editar/<int:id>/', HistorialCargos.historial_cargos_editar, name='historial_cargos_editar'),
    path('historial_cargos/eliminar/', HistorialCargos.historial_cargos_eliminar, name='historial_cargos_eliminar'),
    path('historial_cargos/descargar_excel/', HistorialCargos.historial_cargos_descargar_excel, name='historial_cargos_descargar_excel'),

    # Rutas para la tabla Registro Tiempos
    path('clientes_factura/', ClientesFactura.clientes_factura_index, name='clientes_factura_index'),
    path('clientes_factura/guardar/', ClientesFactura.clientes_factura_guardar, name='clientes_factura_guardar'),
    path('clientes_factura/generar_plantilla/', ClientesFactura.generar_plantilla, name='generar_plantilla'),
    path('clientes_factura/obtener_factura/', ClientesFactura.obtener_tarifa, name='obtener_tarifa'),
    path('clientes_factura/get_lineas_modulos/', ClientesFactura.get_lineas_modulos, name='get_lineas_modulos'),
    path('clientes_factura/eliminar/', ClientesFactura.eliminar_facturas, name='eliminar_facturas'),

    # Rutas para la tabla Facturacion consultores
    path('facturacion_consultores/', FacturacionConsultores.facturacion_consultores, name='facturacion_consultores_index'),
    path('facturacion_consultores/eliminar/', FacturacionConsultores.eliminar_facturacion_consultores, name='eliminar_facturacion_consultores'),
    path('facturacion_consultores/guardar/', FacturacionConsultores.guardar_facturacion_consultores, name='guardar_facturacion_consultores'),

    #Ruta para informe de Facturacion Consultores
    path('Informes/informes_facturacion_consultores/', InformeFacturacionConsultores.informe_totales_por_mes, name='informes_facturacion_consultores_index'),
    path('Informes/informes_facturacion_consultores/reporte_excel_totales_por_mes', InformeFacturacionConsultores.reporte_excel_totales_por_mes , name='reporte_excel_totales_por_mes'),

    # Ruta para informe detalle de Facturacion Consultores
    path('Informes/detalle_facturacion_consultores/', InformeDetalleFacturacionConsultores.informe_detalle_facturacion_consultores, name='informe_detalle_facturacion_consultores_index'),
    path('Informes/detalle_facturacion_consultores/exportar_excel/', InformeDetalleFacturacionConsultores.exportar_detalle_facturacion_consultores_excel, name='exportar_detalle_facturacion_consultores_excel'),

    #Ruta para informe de servicio Facturacion Consultores
    path('Informes/informes_Serv_consultor/', InformeServConsultor.informe_totales, name='informes_serv_consultor_index'),
    path('Informes/informes_Serv_consultor/descargar_informe_totales_excel', InformeServConsultor.descargar_reporte_excel_totales_por_mes, name='descargar_reporte_excel_totales_por_mes'),

    # Rutas para la tabla Indicadores de Operatividad
    path('indicadores_operatividad/', IndicadoresOperatividad.indicadores_operatividad_index, name='indicadores_operatividad_index'),

    # Rutas para la tabla Referencias
    path('referencia/', Referencia.referencia_index, name='referencia_index'),
    path('referencia/crear', Referencia.referencia_crear, name='referencia_crear'),
    path('referencia/editar/<int:id>/', Referencia.referencia_editar, name='referencia_editar'),
    path('referencia/verificar-relaciones/', Referencia.verificar_relaciones, name='verificar_relaciones'),
    path('referencia/eliminar', Referencia.referencia_eliminar, name='referencia_eliminar'),
    path('referencia/descargar_excel', Referencia.referencia_descargar_excel, name='referencia_descargar_excel'),

    # Rutas para la tabla Indicadores de totales
    path('indicadores_totales/', IndicadoresTotales.indicadores_totales, name='indicadores_totales_index'),
    path('indicadores_facturacion/', IndicadoresFacturacion.indicadores_facturacion, name='indicadores_facturacion_index'),
    path('indicadores_margen_cliente/', IndicadoresMargenCliente.indicadores_margen_cliente, name='indicadores_margen_cliente_index'),

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
    path('Informes/pagares/', informe_pagares, name='informe_pagares'),
    path('Informes/pagares/exportar_pagares_excel/', exportar_pagares_excel, name='exportar_pagares_excel'),

    #Ruta para informe de Facturacion Centro Costos
    path('Informes/informe_facturacion_CentroCostos/', InformeFacturacionCentrocostos.informe_facturacion_CentroCostos, name='informe_facturacion_CentroCostos_index'),
    path('Informes/informe_facturacion_CentroCostos/descargar_informe_facturacion_clientes_excel/', InformeFacturacionCentrocostos.descargar_reporte_excel_facturacion_clientes, name='descargar_reporte_excel_facturacion_clientes'),

    # URLs para TipoPagare
    path('TipoPagare/', tipo_pagare_index, name='tipo_pagare_index'),
    path('TipoPagare/crear/', tipo_pagare_crear, name='tipo_pagare_crear'),
    path('TipoPagare/editar/<int:id>/', tipo_pagare_editar, name='tipo_pagare_editar'),
    path('TipoPagare/eliminar/', tipo_pagare_eliminar, name='tipo_pagare_eliminar'),
    path('TipoPagare/confirmar_delete/<int:id>/', tipo_pagare_confirmar_delete, name='tipo_pagare_confirmar_delete'),
    path('TipoPagare/descargar_excel/', tipo_pagare_descargar_excel, name='tipo_pagare_descargar_excel'),

    #Ruta para maestro de linea Cliente CentroCostos
    path('linea_cliente_centrocostos/', LineaClienteCentrocostos.linea_cliente_centrocostos_index, name='linea_cliente_centrocostos_index'),
    path('linea_cliente_centrocostos/crear', LineaClienteCentrocostos.linea_cliente_centrocostos_crear, name='linea_cliente_centrocostos_crear'),
    path('linea_cliente_centrocostos/editar/<int:id>/', LineaClienteCentrocostos.linea_cliente_centrocostos_editar, name='linea_cliente_centrocostos_editar'),
    path('linea_cliente_centrocostos/eliminar', LineaClienteCentrocostos.linea_cliente_centrocostos_eliminar, name='linea_cliente_centrocostos_eliminar'),
    path('linea_cliente_centrocostos/verificar-relaciones/', LineaClienteCentrocostos.linea_cliente_centrocostos_verificar_relaciones, name='linea_cliente_centrocostos_verificar_relaciones'),
    path('linea_cliente_centrocostos/descargar_excel', LineaClienteCentrocostos.linea_cliente_centrocostos_descargar_excel, name='linea_cliente_centrocostos_descargar_excel'),

    # Autenticación
    path('cambiar-password/', AuthViews.cambiar_password, name='cambiar_password'),     

    # Gestión de roles y usuarios
    path('administracion/roles/', AuthViews.role_list, name='role_list'),
    path('administracion/roles/crear/', AuthViews.role_create, name='role_create'),
    path('administracion/roles/editar/<int:role_id>/', AuthViews.role_edit, name='role_edit'),
    path('administracion/roles/eliminar/<int:role_id>/', AuthViews.role_delete, name='role_delete'),
    
    path('administracion/usuarios/', AuthViews.user_list, name='user_list'),
    path('administracion/usuarios/crear/', AuthViews.user_create, name='user_create'),
    path('administracion/usuarios/editar/<int:user_id>/', AuthViews.user_edit, name='user_edit'),
    path('administracion/usuarios/eliminar/<int:user_id>/', AuthViews.user_delete, name='user_delete'),
    
    # Verificación de permisos
    path('check-permission/', AuthViews.check_permission, name='check_permission'),
    path('test-permissions/', AuthViews.test_permissions, name='test_permissions'),
    ]