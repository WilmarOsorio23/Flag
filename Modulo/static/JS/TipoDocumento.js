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

    // Clonar checkboxes seleccionados en el formulario de descarga
    document.getElementById('download-form').addEventListener('submit', function (event) {
        let selectedCheckboxes = document.querySelectorAll('.row-select:checked');
        if (selectedCheckboxes.length === 0) {
            alert('No has seleccionado ningún elemento para descargar.');
            event.preventDefault(); // Evita el envío si no hay elementos seleccionados
            return;
        }

        selectedCheckboxes.forEach(function (checkbox) {
            let clonedCheckbox = checkbox.cloneNode();
            clonedCheckbox.setAttribute('type', 'hidden'); // Ocultarlo en el formulario
            document.getElementById('download-form').appendChild(clonedCheckbox);
        });
    });
    
    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function (event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });

    // Confirmación antes de eliminar
    function confirmDelete() {
        let selected = document.querySelectorAll('.row-select:checked').length;
        if (selected === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return false;
        }
        return confirm('¿Estás seguro de que deseas eliminar los elementos seleccionados?');
    }

    // Habilitar edición en la fila seleccionada
    function enableEdit() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún tipo de documento para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un tipo de documento a la vez.');
            return false;
        }

        let row = selected[0].closest('tr');
        let inputs = row.querySelectorAll('input.form-control-plaintext');
        inputs.forEach(input => {
            input.classList.remove('form-control-plaintext');
            input.classList.add('form-control');
            input.readOnly = false;
        });

        // Mostrar botón de guardar
        document.getElementById('save-button').classList.remove('d-none');
    }

    // Guardar los cambios en la fila seleccionada
    window.saveRow = function () {
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ningún tipo de documento para guardar.');
            return false;
        }

        let row = selected.closest('tr');
        let data = {
            'Nombre': row.querySelector('input[name ="Nombre"]').value
        };
        
        console.log(data)
        let tipoDocumentoID = selected.value;

        console.log(tipoDocumentoID)
        // Enviar datos al servidor
        fetch(`/tipo_documento/editar/${tipoDocumentoID}/`, {
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
                    //inputs.forEach(input => {
                    row.querySelectorAll('input').forEach(input => {
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

});