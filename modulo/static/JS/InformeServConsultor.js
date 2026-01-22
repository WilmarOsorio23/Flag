document.addEventListener('DOMContentLoaded', function () {
    
    // Actualiza el texto del dropdown al seleccionar/desmarcar opciones
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.nextSibling.textContent.trim());

        if (selectedOptions.length === 0) {
            button.textContent = selectedText;
        } else if (selectedOptions.length === 1) {
        button.textContent = selectedOptions[0];
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`;
        }
    }


    // Meses
    const clienteCheckboxes = document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownMes', clienteCheckboxes)
        )
    );

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        )
    );

    // Consultor
    const ConsultorCheckboxes = document.querySelectorAll('#dropdownConsultor ~ .dropdown-menu input[type="checkbox"]');
    ConsultorCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownConsultor', ConsultorCheckboxes)
        )
    );

    function selectAnio(value, label) {
        const button = document.getElementById("dropdownAnio");
        const hiddenInput = document.getElementById("selectedAnio");

        // Actualizar el texto del botón y el valor oculto
        button.textContent = label;
        hiddenInput.value = value;
    }

    // Agregar eventos a cada opción de año
    document.querySelectorAll('.anio-option').forEach(item => {
        item.addEventListener('click', function (event) {
            event.preventDefault(); // Evita que el enlace recargue la página
            selectAnio(this.getAttribute("data-value"), this.textContent);
        });
    });
});
