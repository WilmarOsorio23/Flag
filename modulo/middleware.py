from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.conf import settings

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.permission_mappings = self._build_permission_mappings()
        self.public_urls = ['login', 'logout']
        
    def _build_permission_mappings(self):
        # Construir mapeo dinámico de permisos basado en URLs y nombres de vistas
        mappings = {}
        
        # Mapeo para vistas de Actividades Pagarés
        mappings.update({
            'actividad_pagare_index': 'can_manage_actividades_pagares',
            'actividad_pagare_crear': 'can_manage_actividades_pagares',
            'actividad_pagare_editar': 'can_manage_actividades_pagares',
            'actividad_pagare_eliminar': 'can_manage_actividades_pagares',
        })
        
        # Mapeo para vistas de Maestros
        mappings.update({
            'cargos_index': 'can_manage_cargos',
            'cargos_crear': 'can_manage_cargos',
            'cargos_editar': 'can_manage_cargos',
            'cargos_eliminar': 'can_manage_cargos',
            
            'certificacion_index': 'can_manage_certificacion',
            'certificacion_crear': 'can_manage_certificacion',
            'certificacion_editar': 'can_manage_certificacion',
            'certificacion_eliminar': 'can_manage_certificacion',
            
            'clientes_index': 'can_manage_clientes',
            'clientes_crear': 'can_manage_clientes',
            'clientes_editar': 'can_manage_clientes',
            'clientes_eliminar': 'can_manage_clientes',
            
            'conceptos_index': 'can_manage_conceptos',
            'conceptos_crear': 'can_manage_conceptos',
            'conceptos_editar': 'can_manage_conceptos',
            'conceptos_eliminar': 'can_manage_conceptos',
            
            'consultores_index': 'can_manage_consultores',
            'consultores_crear': 'can_manage_consultores',
            'consultores_editar': 'can_manage_consultores',
            'consultores_eliminar': 'can_manage_consultores',
            
            'contactos_index': 'can_manage_contactos',
            'contactos_crear': 'can_manage_contactos',
            'contactos_editar': 'can_manage_contactos',
            'contactos_eliminar': 'can_manage_contactos',
            
            'costos_indirectos_index': 'can_manage_costos_indirectos',
            'costos_indirectos_crear': 'can_manage_costos_indirectos',
            'costos_indirectos_editar': 'can_manage_costos_indirectos',
            'costos_indirectos_eliminar': 'can_manage_costos_indirectos',
            
            'centros_costos_index': 'can_manage_centros_costos',
            'centros_costos_crear': 'can_manage_centros_costos',
            'centros_costos_editar': 'can_manage_centros_costos',
            'centros_costos_eliminar': 'can_manage_centros_costos',
            
            'empleado_index': 'can_manage_empleados',
            'empleado_crear': 'can_manage_empleados',
            'empleado_editar': 'can_manage_empleados',
            'empleado_eliminar': 'can_manage_empleados',
            
            'empleados_estudios_index': 'can_manage_empleados_estudios',
            'empleados_estudios_crear': 'can_manage_empleados_estudios',
            'empleados_estudios_editar': 'can_manage_empleados_estudios',
            'empleados_estudios_eliminar': 'can_manage_empleados_estudios',
            
            'gastos_index': 'can_manage_gastos',
            'gastos_crear': 'can_manage_gastos',
            'gastos_editar': 'can_manage_gastos',
            'gastos_eliminar': 'can_manage_gastos',
            
            'horas_habiles_index': 'can_manage_horas_habiles',
            'horas_habiles_crear': 'can_manage_horas_habiles',
            'horas_habiles_editar': 'can_manage_horas_habiles',
            'horas_habiles_eliminar': 'can_manage_horas_habiles',
            
            'ind_index': 'can_manage_ind',
            'ind_crear': 'can_manage_ind',
            'ind_editar': 'can_manage_ind',
            'ind_eliminar': 'can_manage_ind',
            
            'ipc_index': 'can_manage_ipc',
            'ipc_crear': 'can_manage_ipc',
            'ipc_editar': 'can_manage_ipc',
            'ipc_eliminar': 'can_manage_ipc',
            
            'linea_index': 'can_manage_linea',
            'linea_crear': 'can_manage_linea',
            'linea_editar': 'can_manage_linea',
            'linea_eliminar': 'can_manage_linea',

            'linea_cliente_centrocostos_index': 'can_manage_linea_cliente_centrocostos',
            'linea_cliente_centrocostos_crear': 'can_manage_linea_cliente_centrocostos',
            'linea_cliente_centrocostos_editar': 'can_manage_linea_cliente_centrocostos',
            'linea_cliente_centrocostos_eliminar': 'can_manage_linea_cliente_centrocostos',
            'linea_cliente_centrocostos_verificar_relaciones': 'can_manage_linea_cliente_centrocostos',
            'linea_cliente_centrocostos_descargar_excel': 'can_manage_linea_cliente_centrocostos',
            
            'modulo_index': 'can_manage_modulo',
            'modulo_crear': 'can_manage_modulo',
            'modulo_editar': 'can_manage_modulo',
            'modulo_eliminar': 'can_manage_modulo',
            
            'moneda_index': 'can_manage_moneda',
            'moneda_crear': 'can_manage_moneda',
            'moneda_editar': 'can_manage_moneda',
            'moneda_eliminar': 'can_manage_moneda',
            
            'perfil_index': 'can_manage_perfil',
            'perfil_crear': 'can_manage_perfil',
            'perfil_editar': 'can_manage_perfil',
            'perfil_eliminar': 'can_manage_perfil',
            
            'referencia_index': 'can_manage_referencias',
            'referencia_crear': 'can_manage_referencias',
            'referencia_editar': 'can_manage_referencias',
            'referencia_eliminar': 'can_manage_referencias',
            
            'tipo_documento_index': 'can_manage_tipo_documento',
            'tipo_documento_crear': 'can_manage_tipo_documento',
            'tipo_documento_editar': 'can_manage_tipo_documento',
            'tipo_documento_eliminar': 'can_manage_tipo_documento',
            
            'tipos_contactos_index': 'can_manage_tipos_contactos',
            'tipos_contactos_crear': 'can_manage_tipos_contactos',
            'tipos_contactos_editar': 'can_manage_tipos_contactos',
            'tipos_contactos_eliminar': 'can_manage_tipos_contactos',
            
            'tipo_pagare_index': 'can_manage_tipo_pagare',
            'tipo_pagare_crear': 'can_manage_tipo_pagare',
            'tipo_pagare_editar': 'can_manage_tipo_pagare',
            'tipo_pagare_eliminar': 'can_manage_tipo_pagare',
        })
        
        # Mapeo para vistas de Movimientos
        mappings.update({
            'clientes_contratos_index': 'can_manage_clientes_contratos',
            'clientes_contratos_crear': 'can_manage_clientes_contratos',
            'clientes_contratos_editar': 'can_manage_clientes_contratos',
            'clientes_contratos_eliminar': 'can_manage_clientes_contratos',
            
            'contratos_otros_si_index': 'can_manage_contratos_otros_si',
            'contratos_otros_si_crear': 'can_manage_contratos_otros_si',
            'contratos_otros_si_editar': 'can_manage_contratos_otros_si',
            'contratos_otros_si_eliminar': 'can_manage_contratos_otros_si',
            
            'pagare_index': 'can_manage_pagare',
            'pagare_crear': 'can_manage_pagare',
            'pagare_editar': 'can_manage_pagare',
            'pagare_eliminar': 'can_manage_pagare',
            'pagare_actualizar': 'can_manage_pagare',
            'pagare_ejecutado': 'can_manage_pagare',
            
            'detalle_certificacion_index': 'can_manage_detalle_certificacion',
            'detalle_certificacion_crear': 'can_manage_detalle_certificacion',
            'detalle_certificacion_editar': 'can_manage_detalle_certificacion',
            'detalle_certificacion_eliminar': 'can_manage_detalle_certificacion',
            
            'detalle_costos_indirectos_index': 'can_manage_detalle_costos_indirectos',
            'detalle_costos_indirectos_crear': 'can_manage_detalle_costos_indirectos',
            'detalle_costos_indirectos_editar': 'can_manage_detalle_costos_indirectos',
            'detalle_costos_indirectos_eliminar': 'can_manage_detalle_costos_indirectos',
            
            'detalle_gastos_index': 'can_manage_detalle_gastos',
            'detalle_gastos_crear': 'can_manage_detalle_gastos',
            'detalle_gastos_editar': 'can_manage_detalle_gastos',
            'detalle_gastos_eliminar': 'can_manage_detalle_gastos',
            
            'historial_cargos_index': 'can_manage_historial_cargos',
            'historial_cargos_crear': 'can_manage_historial_cargos',
            'historial_cargos_editar': 'can_manage_historial_cargos',
            'historial_cargos_eliminar': 'can_manage_historial_cargos',
            
            'nomina_index': 'can_manage_nomina',
            'nomina_crear': 'can_manage_nomina',
            'nomina_editar': 'can_manage_nomina',
            'nomina_eliminar': 'can_manage_nomina',
            
            'registro_tiempos_index': 'can_manage_registro_tiempos',
            'registro_tiempos_crear': 'can_manage_registro_tiempos',
            'registro_tiempos_editar': 'can_manage_registro_tiempos',
            'registro_tiempos_eliminar': 'can_manage_registro_tiempos',
            
            'tarifa_clientes_index': 'can_manage_tarifa_clientes',
            'tarifa_clientes_crear': 'can_manage_tarifa_clientes',
            'tarifa_clientes_editar': 'can_manage_tarifa_clientes',
            'tarifa_clientes_eliminar': 'can_manage_tarifa_clientes',
            
            'tarifa_consultores_index': 'can_manage_tarifa_consultores',
            'tarifa_consultores_crear': 'can_manage_tarifa_consultores',
            'tarifa_consultores_editar': 'can_manage_tarifa_consultores',
            'tarifa_consultores_eliminar': 'can_manage_tarifa_consultores',
            
            'total_costos_indirectos_index': 'can_manage_total_costos_indirectos',
            'total_costos_indirectos_crear': 'can_manage_total_costos_indirectos',
            'total_costos_indirectos_crear_detalle': 'can_manage_total_costos_indirectos',
            'total_costos_indirectos_editar': 'can_manage_total_costos_indirectos',
            'total_costos_indirectos_eliminar': 'can_manage_total_costos_indirectos',
            
            'total_gastos_index': 'can_manage_total_gastos',
            'total_gastos_crear': 'can_manage_total_gastos',
            'total_gastos_crear_detalle': 'can_manage_total_gastos',
            'total_gastos_editar': 'can_manage_total_gastos',
            'total_gastos_eliminar': 'can_manage_total_gastos',
            
            'clientes_factura_index': 'can_manage_clientes_factura',
            'clientes_factura_crear': 'can_manage_clientes_factura',
            'clientes_factura_editar': 'can_manage_clientes_factura',
            'clientes_factura_eliminar': 'can_manage_clientes_factura',
            
            'facturacion_consultores_index': 'can_manage_facturacion_consultores',
            'facturacion_consultores_crear': 'can_manage_facturacion_consultores',
            'facturacion_consultores_editar': 'can_manage_facturacion_consultores',
            'facturacion_consultores_eliminar': 'can_manage_facturacion_consultores',
        })
        
        # Mapeo para vistas de Informes
        mappings.update({
            'informes_certificacion_index': 'can_view_informe_certificacion',
            'informes_empleado_index': 'can_view_informe_empleado',
            'informes_salarios_index': 'can_view_informe_salarios',
            'informes_estudios_index': 'can_view_informe_estudios',
            'informes_consultores_index': 'can_view_informe_consultores',
            'informes_tarifas_consultores_index': 'can_view_informe_tarifas_consultores',
            'informes_facturacion_clientes_index': 'can_view_informe_facturacion',
            'informes_historial_cargos_index': 'can_view_informe_historial_cargos',
            'informes_tarifas_clientes_index': 'can_view_informe_tarifas_clientes',
            'informes_tiempos_consultores': 'can_view_informe_tiempos_consultores',
            'informes_clientes_index': 'can_view_informe_clientes',
            'informes_clientes_contratos_index': 'can_view_informe_clientes_contratos',
            'informes_otros_si_index': 'can_view_informe_otros_si',
            'informe_pagares': 'can_view_informe_pagares',
            'informes_facturacion_consultores_index': 'can_view_informe_facturacion_consultores',
            'informes_serv_consultor_index': 'can_view_informe_serv_consultor',
            'informes_facturacion_centrocostos': 'can_view_informe_facturacion_centrocostos',
            'informe_detalle_facturacion_consultores_index': 'can_view_informe_detalle_facturacion_consultores',
        })
        
        # Mapeo para vistas de Indicadores
        mappings.update({
            'indicadores_operatividad_index': 'can_view_indicadores_operatividad',
            'indicadores_totales_index': 'can_view_indicadores_totales',
            'indicadores_facturacion_index': 'can_view_indicadores_facturacion',
            'indicadores_margen_cliente_index': 'can_view_indicadores_margen_cliente',
        })
        
        # Mapeo para vistas de Administración
        mappings.update({
            'role_list': 'can_manage_roles',
            'role_create': 'can_manage_roles',
            'role_edit': 'can_manage_roles',
            'role_delete': 'can_manage_roles',
            'user_list': 'can_manage_users',
            'user_create': 'can_manage_users',
            'user_edit': 'can_manage_users',
            'user_delete': 'can_manage_users',
            'cambiar_password': 'can_manage_users',
        })
        
        return mappings

    def __call__(self, request):
        # Get the URL name
        resolver_match = resolve(request.path_info)
        url_name = resolver_match.url_name

        # Skip permission check for public URLs
        if url_name in self.public_urls:
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # Super users y staff bypass permission checks
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # Si el usuario no tiene rol, denegar acceso
        if not hasattr(request.user, 'role') or not request.user.role:
            messages.error(request, 'No tiene un rol asignado. Contacte al administrador.')
            return redirect('inicio')

        # Obtener el permiso requerido para esta URL
        required_permission = self.permission_mappings.get(url_name)
        
        # Si no hay permiso mapeado, permitir acceso (o denegar según tu política)
        if not required_permission:
            return self.get_response(request)

        # Verificar si el rol tiene el permiso requerido
        if not getattr(request.user.role, required_permission, False):
            messages.error(request, f'No tiene permiso para acceder a esta sección. Se requiere el permiso: {required_permission}')
            return redirect('inicio')

        return self.get_response(request)