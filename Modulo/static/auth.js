// Function to check if user has permission for a specific feature
async function checkPermission(feature) {
    try {
        const response = await fetch(`/check-permission/?feature=${feature}`);
        const data = await response.json();
        return data.has_permission;
    } catch (error) {
        console.error('Error checking permission:', error);
        return false;
    }
}

// Function to update UI based on user permissions
async function updateUIBasedOnPermissions() {
    // Maestros permissions
    const maestrosElements = document.querySelectorAll('[data-requires-maestros]');
    for (const element of maestrosElements) {
        const permission = element.dataset.requiresMaestros;
        const hasPermission = await checkPermission(`can_manage_${permission}`);
        if (!hasPermission) {
            element.style.display = 'none';
        }
    }

    // Movimientos permissions
    const movimientosElements = document.querySelectorAll('[data-requires-movimientos]');
    for (const element of movimientosElements) {
        const permission = element.dataset.requiresMovimientos;
        const hasPermission = await checkPermission(`can_manage_${permission}`);
        if (!hasPermission) {
            element.style.display = 'none';
        }
    }

    // Informes permissions
    const informesElements = document.querySelectorAll('[data-requires-informes]');
    for (const element of informesElements) {
        const permission = element.dataset.requiresInformes;
        const hasPermission = await checkPermission(`can_view_${permission}`);
        if (!hasPermission) {
            element.style.display = 'none';
        }
    }

    // Indicadores permissions
    const indicadoresElements = document.querySelectorAll('[data-requires-indicadores]');
    for (const element of indicadoresElements) {
        const permission = element.dataset.requiresIndicadores;
        const hasPermission = await checkPermission(`can_view_${permission}`);
        if (!hasPermission) {
            element.style.display = 'none';
        }
    }
}

// Add event listener to update UI when page loads
document.addEventListener('DOMContentLoaded', () => {
    updateUIBasedOnPermissions();
});