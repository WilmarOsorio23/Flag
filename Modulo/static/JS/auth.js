// auth.js
// Mapeo de permisos por categoría
const PERMISSION_CATEGORIES = {
    'administracion': [
        'can_manage_users',
        'can_manage_roles'
    ],
    'maestros': [
        'can_manage_actividades_pagares',
        'can_manage_cargos',
        'can_manage_certificacion',
        'can_manage_clientes',
        'can_manage_conceptos',
        'can_manage_consultores',
        'can_manage_contactos',
        'can_manage_costos_indirectos',
        'can_manage_centros_costos',
        'can_manage_empleados',
        'can_manage_empleados_estudios',
        'can_manage_gastos',
        'can_manage_horas_habiles',
        'can_manage_ind',
        'can_manage_ipc',
        'can_manage_linea',
        'can_manage_modulo',
        'can_manage_moneda',
        'can_manage_perfil',
        'can_manage_referencias',
        'can_manage_tipo_documento',
        'can_manage_tipos_contactos',
        'can_manage_tipo_pagare'
    ],
    'movimientos': [
        'can_manage_clientes_contratos',
        'can_manage_contratos_otros_si',
        'can_manage_pagare',
        'can_manage_detalle_certificacion',
        'can_manage_detalle_costos_indirectos',
        'can_manage_detalle_gastos',
        'can_manage_historial_cargos',
        'can_manage_nomina',
        'can_manage_registro_tiempos',
        'can_manage_tarifa_clientes',
        'can_manage_tarifa_consultores',
        'can_manage_total_costos_indirectos',
        'can_manage_total_gastos',
        'can_manage_clientes_factura',
        'can_manage_facturacion_consultores'
    ],
    'informes': [
        'can_view_informe_certificacion',
        'can_view_informe_empleado',
        'can_view_informe_salarios',
        'can_view_informe_estudios',
        'can_view_informe_consultores',
        'can_view_informe_tarifas_consultores',
        'can_view_informe_facturacion',
        'can_view_informe_historial_cargos',
        'can_view_informe_tarifas_clientes',
        'can_view_informe_tiempos_consultores',
        'can_view_informe_clientes',
        'can_view_informe_clientes_contratos',
        'can_view_informe_otros_si',
        'can_view_informe_pagares',
        'can_view_informe_facturacion_consultores',
        'can_view_informe_serv_consultor',
        'can_view_informe_facturacion_centrocostos',
        'can_view_informe_detalle_facturacion_consultores'
    ],
    'indicadores': [
        'can_view_indicadores_operatividad',
        'can_view_indicadores_totales',
        'can_view_indicadores_facturacion',
        'can_view_indicadores_margen_cliente'
    ]
};

// Función para verificar permisos
async function verificarPermiso(permiso) {
    try {
        const respuesta = await fetch(`/check-permission/?feature=${permiso}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });
        
        if (!respuesta.ok) {
            console.error(`Error HTTP: ${respuesta.status}`);
            return false;
        }
        
        const datos = await respuesta.json();
        return datos.has_permission || false;
    } catch (error) {
        console.error('Error al verificar permisos:', error);
        return false;
    }
}

// Ocultar elementos del menú basado en permisos
async function ocultarElementosNoPermitidos() {
    
    // Verificar permisos para cada categoría
    for (const [categoria, permisos] of Object.entries(PERMISSION_CATEGORIES)) {
        
        // Verificar si el usuario tiene al menos un permiso en esta categoría
        let tieneAcceso = false;
        
        for (const permiso of permisos) {
            const tienePermiso = await verificarPermiso(permiso);
            if (tienePermiso) {
                tieneAcceso = true;
                break;
            }
        }
        
        if (!tieneAcceso) {
            // Ocultar toda la sección del menú
            const seccion = document.querySelector(`[data-categoria="${categoria}"]`);
            if (seccion) {
                seccion.style.display = 'none';
            }
        } else {
            // Ocultar elementos individuales dentro de la sección
            for (const permiso of permisos) {
                const tienePermiso = await verificarPermiso(permiso);
                if (!tienePermiso) {
                    document.querySelectorAll(`[data-requires="${permiso}"]`).forEach(elemento => {
                        elemento.style.display = 'none';
                        // También ocultar el li padre si existe
                        const liPadre = elemento.closest('li');
                        if (liPadre) {
                            liPadre.style.display = 'none';
                        }
                    });
                }
            }
        }
    }
    
    // Verificar elementos individuales sin categoría
    const elementosIndividuales = document.querySelectorAll('[data-requires]');
    for (const elemento of elementosIndividuales) {
        const permiso = elemento.getAttribute('data-requires');
        if (permiso) {
            const tienePermiso = await verificarPermiso(permiso);
            if (!tienePermiso) {
                elemento.style.display = 'none';
                // También ocultar el li padre si existe
                const liPadre = elemento.closest('li');
                if (liPadre) {
                    liPadre.style.display = 'none';
                }
            }
        }
    }
    
    // Verificar si hay submenús vacíos y ocultarlos
    const submenus = document.querySelectorAll('.collapse');
    submenus.forEach(submenu => {
        const elementosVisibles = submenu.querySelectorAll('li:not([style*="display: none"])');
        if (elementosVisibles.length === 0) {
            submenu.style.display = 'none';
            // También ocultar el elemento padre que abre el submenú
            const elementoPadre = submenu.previousElementSibling;
            if (elementoPadre) {
                elementoPadre.style.display = 'none';
            }
        }
    });
    
}

// Iniciar la verificación de permisos
document.addEventListener('DOMContentLoaded', function() {
    ocultarElementosNoPermitidos();
});     