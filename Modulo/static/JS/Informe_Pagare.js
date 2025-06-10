document.addEventListener('DOMContentLoaded', function () {
    function updateDropdownLabel(dropdownId, inputs) {
        const button = document.getElementById(dropdownId);
        const selectedOptions = Array.from(inputs).filter(input => input.checked);
        if (selectedOptions.length === 0) {
            button.textContent = "Seleccione";
        } else if (selectedOptions.length === 1) {
            button.textContent = selectedOptions[0].nextSibling.textContent.trim();
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`;
        }
    }

    function attachDropdownListeners(dropdownId) {
        const inputs = document.querySelectorAll(`#${dropdownId} ~ .dropdown-menu input`);
        inputs.forEach(input => input.addEventListener('change', () => updateDropdownLabel(dropdownId, inputs)));
        updateDropdownLabel(dropdownId, inputs);
    }

    attachDropdownListeners('dropdownEmpleados');
    attachDropdownListeners('dropdownAnio');
    attachDropdownListeners('dropdownLinea');
    attachDropdownListeners('dropdownTipoPagare');

    
});