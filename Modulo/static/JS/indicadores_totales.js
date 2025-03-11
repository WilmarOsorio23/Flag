document.addEventListener('DOMContentLoaded', function() {
    // Actualizar textos de dropdowns
    function actualizarContadorDropdown(buttonId, count) {
        const button = document.getElementById(buttonId);
        const text = button.innerText.split('(')[0].trim();
        button.innerText = count > 0 ? `${text} (${count})` : text;
    }

    // Actualizar todos los contadores
    function actualizarContadores() {
        actualizarContadorDropdown('dropdownMes', document.querySelectorAll('input[name="mes"]:checked').length);
        actualizarContadorDropdown('dropdownLinea', document.querySelectorAll('input[name="linea"]:checked').length);
        actualizarContadorDropdown('dropdownCliente', document.querySelectorAll('input[name="cliente"]:checked').length);
    }

    // Event listeners para cambios en los checkboxes
    document.querySelectorAll('.dropdown-menu input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', actualizarContadores);
    });

    // Inicializar contadores
    actualizarContadores();
});