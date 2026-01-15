// auth.js

const PERMISSION_CATEGORIES = {
    'administracion': ['can_manage_users', 'can_manage_roles'],
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
      'can_manage_linea_cliente_centrocostos',
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
  
  // URL configurable desde base.html
  const CHECK_URL = window.CHECK_PERMISSION_URL || '/check-permission/';
  
  async function fetchPermisos(permisos = []) {
    const unique = Array.from(new Set(permisos)).filter(Boolean);
    if (unique.length === 0) return {};
  
    const url = new URL(CHECK_URL, window.location.origin);
    url.searchParams.set('feature', unique.join(','));
  
    try {
      const resp = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin'
      });
  
      if (!resp.ok) {
        const text = await resp.text().catch(() => '');
        console.error(`Permisos: HTTP ${resp.status}. Respuesta:`, text);
        return {};
      }
  
      const data = await resp.json();
  
      if (data.permissions && typeof data.permissions === 'object') return data.permissions;
      if (typeof data.has_permission === 'boolean' && unique.length === 1) {
        return { [unique[0]]: data.has_permission };
      }
  
      return {};
    } catch (e) {
      console.error('Error consultando permisos:', e);
      return {};
    }
  }
  
  async function ocultarElementosNoPermitidos() {
    const allFromCategories = Object.values(PERMISSION_CATEGORIES).flat();
    const domRequires = Array.from(document.querySelectorAll('[data-requires]'))
      .map(el => el.getAttribute('data-requires'))
      .filter(Boolean);
  
    const allPerms = [...allFromCategories, ...domRequires];
    const permisosMap = await fetchPermisos(allPerms);
  
    // Categorías
    for (const [categoria, permisos] of Object.entries(PERMISSION_CATEGORIES)) {
      const tieneAcceso = permisos.some(p => permisosMap[p] === true);
      const seccion = document.querySelector(`[data-categoria="${categoria}"]`);
  
      if (!tieneAcceso) {
        if (seccion) seccion.style.display = 'none';
        continue;
      }
  
      // Items individuales
      for (const permiso of permisos) {
        if (permisosMap[permiso] !== true) {
          document.querySelectorAll(`[data-requires="${permiso}"]`).forEach(el => {
            el.style.display = 'none';
            const li = el.closest('li');
            if (li) li.style.display = 'none';
          });
        }
      }
    }
  
    // Elementos sueltos
    document.querySelectorAll('[data-requires]').forEach(el => {
      const permiso = el.getAttribute('data-requires');
      if (permiso && permisosMap[permiso] !== true) {
        el.style.display = 'none';
        const li = el.closest('li');
        if (li) li.style.display = 'none';
      }
    });
  
    // Submenús vacíos
    document.querySelectorAll('.collapse').forEach(submenu => {
      const visibles = submenu.querySelectorAll('li:not([style*="display: none"])');
      if (visibles.length === 0) {
        submenu.style.display = 'none';
        const padre = submenu.previousElementSibling;
        if (padre) padre.style.display = 'none';
      }
    });
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    ocultarElementosNoPermitidos();
  });
  