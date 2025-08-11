// Función para verificar permisos
async function verificarPermiso(permiso) {
    try {
        const respuesta = await fetch(`/check-permission/?feature=${permiso}`);
        const datos = await respuesta.json();
        return datos.has_permission;
    } catch (error) {
        console.error('Error al verificar permisos:', error);
        return false;
    }
}

// Ocultar elementos del menú basado en permisos
async function ocultarElementosNoPermitidos() {
    // Verificar permisos para elementos de Maestros
    document.querySelectorAll('[data-requires-maestros]').forEach(async (elemento) => {
        const permiso = 'can_manage_' + elemento.dataset.requiresMaestros;
        const tienePermiso = await verificarPermiso(permiso);
        if (!tienePermiso) {
            elemento.style.display = 'none';
        }
    });

    // Verificar permisos para elementos de Movimientos
    document.querySelectorAll('[data-requires-movimientos]').forEach(async (elemento) => {
        const permiso = 'can_manage_' + elemento.dataset.requiresMovimientos;
        const tienePermiso = await verificarPermiso(permiso);
        if (!tienePermiso) {
            elemento.style.display = 'none';
        }
    });

    // Verificar permisos para elementos de Informes
    document.querySelectorAll('[data-requires-informes]').forEach(async (elemento) => {
        const permiso = 'can_view_informe_' + elemento.dataset.requiresInformes;
        const tienePermiso = await verificarPermiso(permiso);
        if (!tienePermiso) {
            elemento.style.display = 'none';
        }
    });

    // Verificar permisos para elementos de Indicadores
    document.querySelectorAll('[data-requires-indicadores]').forEach(async (elemento) => {
        const permiso = 'can_view_indicadores_' + elemento.dataset.requiresIndicadores;
        const tienePermiso = await verificarPermiso(permiso);
        if (!tienePermiso) {
            elemento.style.display = 'none';
        }
    });
}

// Iniciar la verificación de permisos
document.addEventListener('DOMContentLoaded', function() {
    ocultarElementosNoPermitidos();
});