
    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function(event) {
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
            alert('No has seleccionado ninguna nómina para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar una nómina a la vez.');
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
    function saveRow() {
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ninguna nómina para guardar.');
            return false;
        }

        let row = selected.closest('tr');
        let inputs = row.querySelectorAll('input.form-control');
        let data = {};

        inputs.forEach(input => {
            let name = input.getAttribute('name');
            data[name] = input.value;
        });

        let nominaId = selected.value.split('|');
        let editUrl = `/nomina/editar/${nominaId[0]}/${nominaId[1]}/${nominaId[2]}/`;

        // Enviar datos al servidor
        fetch(editUrl, {
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
