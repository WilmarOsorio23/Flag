
   
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
    window.enableEdit = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún IPC para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un IPC a la vez.');
            return false;
        }

        let row = selected[0].closest('tr');
        let inputs = row.querySelectorAll('input.form-control-plaintext');

        // Guardar valores originales en un atributo personalizado 
        inputs.forEach(input => { 
        input.setAttribute('data-original-value', input.value);
        });

        // Desactivar todos los checkboxes, incluyendo el de seleccionar todos, boton de editar  
        document.getElementById('select-all').disabled = true;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        // Convertir inputs en editables
        let input = row.querySelector('[name ="Indice"]');
         input.classList.remove('form-control-plaintext');
         input.classList.add('form-control');
         input.readOnly = false;
         

        // Mostrar botones de "Guardar" y "Cancelar" en la parte superior
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');

    };

    // Guardar los cambios en la fila seleccionada
    function saveRow() {
    
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ningún IPC para guardar.');
            return false;
        }
        let row = selected.closest('tr');
        let data={
            'Anio': row.querySelector('input[name ="Anio"]').value,
            'Mes': row.querySelector('input[name ="Mes"]').value,
            'Indice': row.querySelector('input[name ="Indice"]').value
        }
        console.log(data);
        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;
        
        let ipcId = selected.value;
      
        console.log(ipcId);
        // Enviar datos al servidor
        fetch(`/ipc/editar/${ipcId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then((response) => response.json())
        .then(data => {
            if (data.status == 'success') {
                showMessage('Cambios guardados correctamente.', 'success');

                row.querySelectorAll('input.form-control').forEach(input => {
                    input.classList.add('highlighted');
                    setTimeout(() => input.classList.remove('highlighted'), 2000);
                });

                disableEditMode(selected,row);

            } else {
                showMessage('Error al guardar los cambios: ' + (data.error || 'Error desconocido'), 'danger');
            }

        })
        .catch(error => {
            console.error('Error al guardar los cambios:', error);
            showMessage('Error al guardar los cambios: ' + error.message, 'danger');

            disableEditMode(selected,row);
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
    

    // Prevenir la acción predeterminada al presionar Enter en cualquier parte de la página
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            // Verifica si el foco está en un botón o enlace específico
            let isButtonOrLink = event.target.tagName === 'BUTTON' || event.target.tagName === 'A';
            
            // Si no es un botón o enlace, previene el envío del formulario
            if (!isButtonOrLink) {
                event.preventDefault();
            }
        }
    });

    window.cancelEdit = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length == 1) {
           
            let row = selected[0].closest('tr');

            // Restaurar los valores originales desde el atributo personalizado
            row.querySelectorAll('input.form-control').forEach(input => {
                if (input.hasAttribute('data-original-value')) {
                    input.value = input.getAttribute('data-original-value');
                }
            });
            
            disableEditMode(selected,row);
            showMessage('Cambios cancelados.', 'danger');
        }
    };

    
        // Deshabilitar modo edición
    function disableEditMode(selected,row) {
        // Cambiar inputs a solo lectura
        console.log("llego hasta aca")
        row.querySelectorAll('input.form-control').forEach(input => {
            input.classList.add('form-control-plaintext');
            input.classList.remove('form-control');
            input.readOnly = true;
        });

        // Desmarcar y habilitar el checkbox de la fila
        selected[0].checked = false;
        selected[0].disabled = false;

        // Habilitar todos los checkboxes y el botón de edición
        document.getElementById('select-all').disabled = false;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = false);
        document.getElementById('edit-button').disabled = false;

        // Ocultar los botones de guardar y cancelar
        document.getElementById('save-button').classList.add('d-none');
        document.getElementById('cancel-button').classList.add('d-none');
    }

    function showMessage(message, type) {
        const alertBox = document.getElementById('message-box');
        const alertIcon = document.getElementById('alert-icon');
        const alertMessage = document.getElementById('alert-message');

        // Asignar el mensaje y el tipo de alerta
        alertMessage.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;

        // Asignar íconos según el tipo
        const icons = {
            success: '✔️', // Puedes usar clases de FontAwesome o Bootstrap Icons
            danger: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        alertIcon.textContent = icons[type] || '';

        // Mostrar la alerta
        alertBox.style.display = 'block';

        // Ocultar la alerta después de 3 segundos
        setTimeout(() => {
            alertBox.classList.remove('show');
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 300); // Tiempo para que la transición termine
        }, 3000);
    }

    // Confirmación antes de descargar
    window.confirmDownload = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length == 0) {
            showMessage('No has seleccionado ningún elemento para descargar.', 'danger');
            return false;
        }

        let itemIds = [];
        selected.forEach(function(checkbox) {
            itemIds.push(checkbox.value);
        });
        document.getElementById('items_to_delete').value = itemIds.join(',');

        return true;
    };
