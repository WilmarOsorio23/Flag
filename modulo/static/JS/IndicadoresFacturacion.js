document.addEventListener('DOMContentLoaded', function() {// Inicializar tabs
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
    
}); 