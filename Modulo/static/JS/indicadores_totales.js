document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tabs
    const triggerTabList = [].slice.call(document.querySelectorAll('#myTab button'))
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl)
        triggerEl.addEventListener('click', event => {
            event.preventDefault()
            tabTrigger.show()
        })
    })
    
    // Actualiza el texto del dropdown al seleccionar/desmarcar opciones
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.nextSibling.textContent.trim());
        
        button.textContent = selectedOptions.length > 0
            ? selectedOptions.join(', ')    
            : selectedText;
    }

    // Meses
    const mesCheckboxes = document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]');
    mesCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownMes', mesCheckboxes)
        )
    );

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        )
    );

    // Clientes
    const clienteCheckboxes = document.querySelectorAll('#dropdownCliente ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownCliente', clienteCheckboxes)
        )
    );
});

document.querySelectorAll('input[data-toggle-partner]').forEach(input => {
    input.addEventListener('input', function(e) {
        const targetName = e.target.dataset.togglePartner;
        const targetInput = document.querySelector(`[name="${targetName}"]`);
        
        // Lógica de deshabilitación
        if (e.target.value !== "" && e.target.value > 0) {
            targetInput.disabled = true;
            targetInput.value = "";
        } else {
            targetInput.disabled = false;
        }
    });
    
    // Inicializar estado
    const partnerName = input.dataset.togglePartner;
    const partnerInput = document.querySelector(`[name="${partnerName}"]`);
    partnerInput.disabled = input.value !== "" && input.value > 0;
});