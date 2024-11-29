document.addEventListener('DOMContentLoaded', function () {
    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Prevenir el envío del formulario al presionar la tecla Enter
    function preventFormSubmissionOnEnter() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', function (event) {
                if (event.key == "Enter") {
                    event.preventDefault(); // Prevenir la acción predeterminada de la tecla Enter
                }
            });
        });
    }
    
    // Guardar los cambios en la fila seleccionada
    function saveConceptRow() {
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ningún concepto para guardar.');
            return false;
        }

        let row = selected.closest('tr');
        let inputs = row.querySelectorAll('input.form-control');
        let data = {};

        inputs.forEach(input => {
            let name = input.getAttribute('name');
            data[name] = input.value;
        });

        let conceptoId = selected.value;

        // Enviar datos al servidor
        fetch(`/conceptos/editar/${conceptoId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Volver a modo de solo lectura
                inputs.forEach(input => {
                    input.classList.add('form-control-plaintext');
                    input.classList.remove('form-control');
                    input.readOnly = true;
                });

                // Ocultar botón de guardar
                document.getElementById('save-button').classList.add('d-none');
            } else {
                alert('Error al guardar los cambios: ' + JSON.stringify(data.errors));
            }
        })
        .catch(error => {
            alert('Error al enviar los datos: ' + error.message);
        });

        return false;
    }

    // Clonar checkboxes seleccionados en el formulario de descarga
    document.getElementById('download-form').addEventListener('submit', function(event) {
        let selectedCheckboxes = document.querySelectorAll('.row-select:checked');
        if (selectedCheckboxes.length === 0) {
            alert('No has seleccionado ningún elemento para descargar.');
            event.preventDefault(); // Evita el envío si no hay elementos seleccionados
            return;
        }

        selectedCheckboxes.forEach(function(checkbox) {
            let clonedCheckbox = checkbox.cloneNode();
            clonedCheckbox.setAttribute('type', 'hidden'); // Ocultarlo en el formulario
            document.getElementById('download-form').appendChild(clonedCheckbox);
        });
    });

    document.getElementById('select-all').addEventListener('click', function(event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });

    function confirmDelete() {
        let selected = document.querySelectorAll('.row-select:checked').length;
        if (selected === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return false;
        }
        return confirm('¿Estás seguro de que deseas eliminar los elementos seleccionados?');
    }

    function handleEditClick() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún concepto para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un concepto a la vez.');
            return false;
        }

        let selectedId = selected[0].value;
        let editUrl = "{% url 'conceptos_editar' 0 %}".replace('0', selectedId);
        window.location.href = editUrl;
    }
});