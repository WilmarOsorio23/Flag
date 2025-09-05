from django.core.management.base import BaseCommand
from Modulo.models import UserRole

class Command(BaseCommand):
    help = 'Initialize predefined roles with their permissions'
    
    def handle(self, *args, **options):
        # Rol de Administrador (acceso total)
        admin_role, created = UserRole.objects.get_or_create(
            name='Administrador',
            defaults={
                'description': 'Acceso completo a todas las funcionalidades del sistema',
            }
        )
        
        if created:
            # Establecer todos los permisos en True
            for field in admin_role._meta.fields:
                if field.name.startswith('can_'):
                    setattr(admin_role, field.name, True)
            admin_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Administrador creado con todos los permisos'))
        
        # Rol de Gestión Humana
        gh_role, created = UserRole.objects.get_or_create(
            name='Gestión Humana',
            defaults={
                'description': 'Acceso a módulos de gestión humana',
                # Actividades pagarés
                'can_manage_actividades_pagares': True,
                'can_manage_pagare': True,
                'can_manage_tipo_pagare': True,
                # Maestros
                'can_manage_cargos': True,
                'can_manage_certificacion': True,
                'can_manage_empleados': True,
                'can_manage_empleados_estudios': True,
                'can_manage_horas_habiles': True,
                'can_manage_perfil': True,
                'can_manage_historial_cargos': True,
                'can_manage_detalle_certificacion': True,
                # Informes
                'can_view_informe_certificacion': True,
                'can_view_informe_empleado': True,
                'can_view_informe_estudios': True,
                'can_view_informe_consultores': True,
                'can_view_informe_historial_cargos': True,
                'can_view_informe_pagares': True,
            }
        )
        
        if created:
            gh_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Gestión Humana creado'))
        
        # Rol de Gestión Administrativa
        ga_role, created = UserRole.objects.get_or_create(
            name='Gestión Administrativa',
            defaults={
                'description': 'Acceso a módulos administrativos y de clientes',
                # Maestros
                'can_manage_clientes': True,
                'can_manage_consultores': True,
                'can_manage_contactos': True,
                'can_manage_costos_indirectos': True,
                'can_manage_centros_costos': True,
                'can_manage_gastos': True,
                'can_manage_ind': True,
                'can_manage_ipc': True,
                'can_manage_referencias': True,
                'can_manage_tipo_pagare': True,
                # Movimientos
                'can_manage_clientes_contratos': True,
                'can_manage_contratos_otros_si': True,
                'can_manage_pagare': True,
                'can_manage_detalle_costos_indirectos': True,
                'can_manage_detalle_gastos': True,
                'can_manage_nomina': True,
                'can_manage_tarifa_clientes': True,
                'can_manage_tarifa_consultores': True,
                'can_manage_total_costos_indirectos': True,
                'can_manage_total_gastos': True,
                'can_manage_facturacion_consultores': True,
                # Informes
                'can_view_informe_salarios': True,
                'can_view_informe_tarifas_consultores': True,
                'can_view_informe_tarifas_clientes': True,
                'can_view_informe_tiempos_consultores': True,
                'can_view_informe_clientes': True,
                'can_view_informe_clientes_contratos': True,
                'can_view_informe_otros_si': True,
                'can_view_informe_facturacion_consultores': True,
                'can_view_informe_serv_consultor': True,
                'can_view_informe_facturacion_clientes': True,
                # Indicadores
                'can_view_indicadores_operatividad': True,
                'can_view_indicadores_totales': True,
                'can_view_indicadores_facturacion': True,
                'can_view_indicadores_margen_cliente': True,
            }
        )
        
        if created:
            ga_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Gestión Administrativa creado'))
        
        # Rol de Líder Servicio
        ls_role, created = UserRole.objects.get_or_create(
            name='Líder Servicio',
            defaults={
                'description': 'Acceso a módulos de liderazgo y coordinación',
                # Actividades pagarés
                'can_manage_actividades_pagares': True,
                'can_manage_pagare': True,
                'can_manage_tipo_pagare': True,
                # Maestros
                'can_manage_cargos': True,
                'can_manage_certificacion': True,
                'can_manage_clientes': True,
                'can_manage_conceptos': True,
                'can_manage_consultores': True,
                'can_manage_contactos': True,
                'can_manage_costos_indirectos': True,
                'can_manage_centros_costos': True,
                'can_manage_empleados': True,
                'can_manage_empleados_estudios': True,
                'can_manage_gastos': True,
                'can_manage_horas_habiles': True,
                'can_manage_ind': True,
                'can_manage_ipc': True,
                'can_manage_linea': True,
                'can_manage_modulo': True,
                'can_manage_moneda': True,
                'can_manage_perfil': True,
                'can_manage_referencias': True,
                'can_manage_tipo_documento': True,
                'can_manage_tipos_contactos': True,
                'can_manage_tipo_pagare': True,
                # Movimientos
                'can_manage_clientes_contratos': True,
                'can_manage_contratos_otros_si': True,
                'can_manage_detalle_certificacion': True,
                'can_manage_detalle_costos_indirectos': True,
                'can_manage_detalle_gastos': True,
                'can_manage_historial_cargos': True,
                'can_manage_nomina': True,
                'can_manage_registro_tiempos': True,
                'can_manage_tarifa_clientes': True,
                'can_manage_tarifa_consultores': True,
                'can_manage_total_costos_indirectos': True,
                'can_manage_total_gastos': True,
                'can_manage_facturacion_consultores': True,
                # Informes
                'can_view_informe_certificacion': True,
                'can_view_informe_empleado': True,
                'can_view_informe_salarios': True,
                'can_view_informe_estudios': True,
                'can_view_informe_consultores': True,
                'can_view_informe_tarifas_consultores': True,
                'can_view_informe_tarifas_clientes': True,
                'can_view_informe_tiempos_consultores': True,
                'can_view_informe_clientes': True,
                'can_view_informe_clientes_contratos': True,
                'can_view_informe_otros_si': True,
                'can_view_informe_pagares': True,
                'can_view_informe_facturacion_consultores': True,
                'can_view_informe_serv_consultor': True,
                'can_view_informe_facturacion_clientes': True,
                # Indicadores
                'can_view_indicadores_operatividad': True,
                'can_view_indicadores_totales': True,
                'can_view_indicadores_facturacion': True,
                'can_view_indicadores_margen_cliente': True,
            }
        )
        
        if created:
            ls_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Líder Servicio creado'))
        
        # Rol de Coordinador
        coord_role, created = UserRole.objects.get_or_create(
            name='Coordinador',
            defaults={
                'description': 'Acceso a módulos de coordinación y seguimiento',
                # Actividades pagarés
                'can_manage_actividades_pagares': True,
                'can_manage_pagare': True,
                'can_manage_tipo_pagare': True,
                # Maestros
                'can_manage_cargos': True,
                'can_manage_certificacion': True,
                'can_manage_clientes': True,
                'can_manage_conceptos': True,
                'can_manage_consultores': True,
                'can_manage_contactos': True,
                'can_manage_costos_indirectos': True,
                'can_manage_centros_costos': True,
                'can_manage_empleados': True,
                'can_manage_empleados_estudios': True,
                'can_manage_gastos': True,
                'can_manage_horas_habiles': True,
                'can_manage_ind': True,
                'can_manage_ipc': True,
                'can_manage_linea': True,
                'can_manage_modulo': True,
                'can_manage_moneda': True,
                'can_manage_perfil': True,
                'can_manage_referencias': True,
                'can_manage_tipo_documento': True,
                'can_manage_tipos_contactos': True,
                'can_manage_tipo_pagare': True,
                # Movimientos
                'can_manage_clientes_contratos': True,
                'can_manage_contratos_otros_si': True,
                'can_manage_detalle_certificacion': True,
                'can_manage_detalle_costos_indirectos': True,
                'can_manage_detalle_gastos': True,
                'can_manage_historial_cargos': True,
                'can_manage_nomina': True,
                'can_manage_registro_tiempos': True,
                'can_manage_tarifa_clientes': True,
                'can_manage_tarifa_consultores': True,
                'can_manage_total_costos_indirectos': True,
                'can_manage_total_gastos': True,
                'can_manage_facturacion_consultores': True,
                # Informes
                'can_view_informe_certificacion': True,
                'can_view_informe_empleado': True,
                'can_view_informe_salarios': True,
                'can_view_informe_estudios': True,
                'can_view_informe_consultores': True,
                'can_view_informe_tarifas_consultores': True,
                'can_view_informe_tarifas_clientes': True,
                'can_view_informe_tiempos_consultores': True,
                'can_view_informe_clientes': True,
                'can_view_informe_clientes_contratos': True,
                'can_view_informe_otros_si': True,
                'can_view_informe_pagares': True,
                'can_view_informe_facturacion_consultores': True,
                'can_view_informe_serv_consultor': True,
                'can_view_informe_facturacion_clientes': True,
                # Indicadores
                'can_view_indicadores_operatividad': True,
                'can_view_indicadores_totales': True,
                'can_view_indicadores_facturacion': True,
                'can_view_indicadores_margen_cliente': True,
            }
        )
        
        if created:
            coord_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Coordinador creado'))
        
        # Rol de Gerencia
        ger_role, created = UserRole.objects.get_or_create(
            name='Gerencia',
            defaults={
                'description': 'Acceso a módulos de gerencia y reportes ejecutivos',
                # Maestros
                'can_manage_clientes': True,
                'can_manage_consultores': True,
                'can_manage_contactos': True,
                'can_manage_costos_indirectos': True,
                'can_manage_centros_costos': True,
                'can_manage_gastos': True,
                'can_manage_ind': True,
                'can_manage_ipc': True,
                'can_manage_linea': True,
                'can_manage_modulo': True,
                'can_manage_moneda': True,
                'can_manage_referencias': True,
                'can_manage_tipo_documento': True,
                'can_manage_tipos_contactos': True,
                'can_manage_tipo_pagare': True,
                # Movimientos
                'can_manage_clientes_contratos': True,
                'can_manage_contratos_otros_si': True,
                'can_manage_detalle_costos_indirectos': True,
                'can_manage_detalle_gastos': True,
                'can_manage_nomina': True,
                'can_manage_tarifa_clientes': True,
                'can_manage_tarifa_consultores': True,
                'can_manage_total_costos_indirectos': True,
                'can_manage_total_gastos': True,
                'can_manage_clientes_factura': True,
                'can_manage_facturacion_consultores': True,
                # Informes
                'can_view_informe_certificacion': True,
                'can_view_informe_empleado': True,
                'can_view_informe_salarios': True,
                'can_view_informe_estudios': True,
                'can_view_informe_consultores': True,
                'can_view_informe_tarifas_consultores': True,
                'can_view_informe_facturacion': True,
                'can_view_informe_historial_cargos': True,
                'can_view_informe_tarifas_clientes': True,
                'can_view_informe_tiempos_consultores': True,
                'can_view_informe_clientes': True,
                'can_view_informe_clientes_contratos': True,
                'can_view_informe_otros_si': True,
                'can_view_informe_pagares': True,
                'can_view_informe_facturacion_consultores': True,
                'can_view_informe_serv_consultor': True,
                'can_view_informe_facturacion_clientes': True,
                # Indicadores
                'can_view_indicadores_operatividad': True,
                'can_view_indicadores_totales': True,
                'can_view_indicadores_facturacion': True,
                'can_view_indicadores_margen_cliente': True,
            }
        )
        
        if created:
            ger_role.save()
            self.stdout.write(self.style.SUCCESS('Rol Gerencia creado'))
        
        self.stdout.write(self.style.SUCCESS('Todos los roles han sido inicializados correctamente'))