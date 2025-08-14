from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.conf import settings

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that don't require permission checks
        self.public_urls = [
            'login',
            'logout',
            'check-permission',
        ]
        
        # Permission mappings
        self.permission_mappings = {
            # Maestros
            'modulo': 'can_manage_modulo',
            'linea': 'can_manage_linea',
            'perfil': 'can_manage_perfil',
            'tipo_documento': 'can_manage_tipo_documento',
            'cargos': 'can_manage_cargos',
            'clientes': 'can_manage_clientes',
            'consultores': 'can_manage_consultores',
            'certificacion': 'can_manage_certificacion',
            'costos_indirectos': 'can_manage_costos_indirectos',
            'conceptos': 'can_manage_conceptos',
            'gastos': 'can_manage_gastos',
            
            # Movimientos
            'clientes_contratos': 'can_manage_clientes_contratos',
            'detalle_certificacion': 'can_manage_detalle_certificacion',
            'detalle_costos_indirectos': 'can_manage_detalle_costos_indirectos',
            'detalle_gastos': 'can_manage_detalle_gastos',
            'historial_cargos': 'can_manage_historial_cargos',
            'nomina': 'can_manage_nomina',
            'registro_tiempos': 'can_manage_registro_tiempos',
            'tarifa_clientes': 'can_manage_tarifa_clientes',
            'tarifa_consultores': 'can_manage_tarifa_consultores',
            'facturacion_clientes': 'can_manage_facturacion_clientes',
            'facturas_consultores': 'can_manage_facturas_consultores',
            'pagares': 'can_manage_pagares',
            
            # Informes
            'informes/certificaciones': 'can_view_informe_certificaciones',
            'informes/empleados': 'can_view_informe_empleados',
            'informes/salarios': 'can_view_informe_salarios',
            'informes/estudios': 'can_view_informe_estudios',
            'informes/consultores': 'can_view_informe_consultores',
            'informes/tarifas_consultores': 'can_view_informe_tarifa_consultores',
            'informes/tarifas_clientes': 'can_view_informe_tarifa_clientes',
            'informes/facturacion': 'can_view_informe_facturacion',
            'informes/clientes': 'can_view_informe_clientes',
            
            # Indicadores
            'indicadores_operatividad': 'can_view_indicadores_operatividad',
            'indicadores_rentabilidad': 'can_view_indicadores_rentabilidad',
            'indicadores_facturacion': 'can_view_indicadores_facturacion',
            'indicadores_margen_linea': 'can_view_indicadores_margen_linea',
            'indicadores_margen_cliente': 'can_view_indicadores_margen_cliente',
            
            # URLs de administración
            'user_list': 'can_manage_users',
            'user_create': 'can_manage_users',
            'user_edit': 'can_manage_users',
            'user_delete': 'can_manage_users',
            'role_list': 'can_manage_roles',
            'role_create': 'can_manage_roles',
            'role_edit': 'can_manage_roles',
        }

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
            messages.error(request, 'No tiene un rol asignado.')
            return redirect('inicio')

        # Obtener el permiso requerido para esta URL
        required_permission = self.permission_mappings.get(url_name)
        
        # Si no hay permiso mapeado, permitir acceso (o denegar según tu política)
        if not required_permission:
            return self.get_response(request)

        # Verificar si el rol tiene el permiso requerido
        if not getattr(request.user.role, required_permission, False):
            messages.error(request, 'No tiene permiso para acceder a esta sección.')
            return redirect('inicio')

        return self.get_response(request)