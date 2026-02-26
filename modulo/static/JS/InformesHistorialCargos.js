document.addEventListener('DOMContentLoaded', function () {
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes).filter(checkbox => checkbox.checked);

        if (selectedOptions.length === 0) {
            button.textContent = selectedText; // Texto por defecto
        } else if (selectedOptions.length === 1) {
            button.textContent = selectedOptions[0].nextSibling.textContent.trim(); // Nombre único seleccionado
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`; // "n seleccionados"
        }
    }

    function attachDropdownListeners(dropdownId) {
        const checkboxes = document.querySelectorAll(`#${dropdownId} ~ .dropdown-menu input[type="checkbox"]`);
        checkboxes.forEach(checkbox =>
            checkbox.addEventListener('change', () => updateDropdownLabel(dropdownId, checkboxes))
        );
        updateDropdownLabel(dropdownId, checkboxes);
    }

    attachDropdownListeners('dropdownEmpleado');
    attachDropdownListeners('dropdownCargo');
    attachDropdownListeners('dropdownLinea');
    
});
