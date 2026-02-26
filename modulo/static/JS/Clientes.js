document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');

    document.getElementById('select-all').addEventListener('click', toggleCheckboxSelection);
    document.querySelector('.btn-outline-danger.fas.fa-trash-alt').addEventListener('click', function (event) {
        handleDeleteConfirmation(event, confirmDeleteModal, confirmDeleteButton, deleteForm, csrfToken);
    });

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

    function toggleCheckboxSelection(event) {
        const checkboxes = document.querySelectorAll('.row-select');
        checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
    }

    // Clonar checkboxes seleccionados en el formulario de descarga
    document.getElementById('download-form').addEventListener('submit', function (event) {
        let selectedCheckboxes = document.querySelectorAll('.row-select:checked');
        if (selectedCheckboxes.length === 0) {
            alert('No has seleccionado ningún elemento para descargar.');
            event.preventDefault(); // Evita el envío si no hay elementos seleccionados
            return;
        }

        // Captura los valores de los checkboxes seleccionados
        let selectedValues = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
    
        // Asigna los valores seleccionados al campo oculto
        document.getElementById('items_to_delete').value = selectedValues.join(',');

        /*Limpiar cualquier checkbox previamente clonado
        document.querySelectorAll('#download-form input[type="checkbox"]').forEach(checkbox => checkbox.remove());


        selectedCheckboxes.forEach(function (checkbox) {
            let clonedCheckbox = checkbox.cloneNode();
            clonedCheckbox.setAttribute('type', 'hidden'); // Ocultarlo en el formulario
            document.getElementById('download-form').appendChild(clonedCheckbox);
        });*/
    });

    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function (event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });



    document.querySelectorAll('select[name="ContactoID"]').forEach(select => {
        select.addEventListener('focus', function () {
            const clienteId = this.closest('tr').querySelector('input[name="items_to_delete"]').value;
            const contactos = contactosPorCliente[clienteId] || [];
            this.innerHTML = ''; // Limpiar opciones anteriores
            contactos.forEach(contacto => {
                const option = document.createElement('option');
                option.value = contacto.id;
                option.textContent = contacto.Nombre;
                this.appendChild(option);
            });
        });
    });


    // Confirmación antes de eliminar
    window.confirmDelete = function () {
        let selected = document.querySelectorAll('.row-select:checked').length;
        if (selected === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return false;
        }
        return confirm('¿Estás seguro de que deseas eliminar los elementos seleccionados?');
    };

    // Confirmación antes de descargar
    window.confirmDownload = function () {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún elemento para descargar.');
            return false;
        }

        let itemIds = [];
        selected.forEach(function (checkbox) {
            itemIds.push(checkbox.value);
        });
        document.getElementById('items_to_delete').value = itemIds.join(',');

        return true; // Permitir la descarga si hay elementos seleccionados
    };

    // Habilitar edición en la fila seleccionada
    window.enableEdit = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length == 0) {
            showMessage('Por favor, selecciona al menos un Cliente.', 'danger');
            return false;
        }
        if (selected.length > 1) {
            showMessage('Por favor, Selecciona un solo cliente para editar.', 'danger');
            return false;
        }

        let row = selected[0].closest('tr');
        let inputs = row.querySelectorAll('input.form-control-plaintext');
        let selects = row.querySelectorAll('select.form-control-plaintext');

        // Guardar valores originales en un atributo personalizado 
        inputs.forEach(input => { 
            input.setAttribute('data-original-value', input.value);
        });

        selects.forEach(select => {
            select.setAttribute('data-original-value', select.value);
        });

        // Desactivar todos los checkboxes, incluyendo el de seleccionar todos, boton de editar  
        document.getElementById('select-all').disabled = true;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        selects.forEach(select => {
            select.classList.remove("form-control-plaintext");
            select.classList.add("form-control");
            select.removeAttribute("disabled");
        });

        // Convertir inputs en editables
        inputs.forEach(input => {
            input.classList.remove('form-control-plaintext');
            input.classList.add('form-control');
            input.readOnly = false;
        });

        // Mostrar botones de "Guardar" y "Cancelar" en la parte superior
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');

    };
    

    // Guardar los cambios en la fila seleccionada
    window.saveRow = function() {        
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length != 1) {
            showMessage('Error al guardar: No hay un detalle seleccionado.', 'danger');
            return;
        }

        
        let row = selected[0].closest('tbody tr');       
        let data = {
            'Nombre_Cliente': row.querySelector('input[name ="Nombre_Cliente"]').value,
            'Activo': row.querySelector('select[name="Activo"]').value,
            'Fecha_Inicio': row.querySelector('input[name ="Fecha_Inicio"]').value,
            'Fecha_Retiro': row.querySelector('input[name="Fecha_Retiro"]').value || null,
            'Direccion': row.querySelector('input[name ="Direccion"]').value || null,
            'Telefono': row.querySelector('input[name ="Telefono"]').value || null,
            'CorreoElectronico': row.querySelector('input[name ="CorreoElectronico"]').value || null,
            'BuzonFacturacion': row.querySelector('input[name ="BuzonFacturacion"]').value || null,
            'TipoCliente': row.querySelector('input[name ="TipoCliente"]').value || null,
            'Ciudad': row.querySelector('input[name ="Ciudad"]').value || null,
            'Departamento': row.querySelector('input[name ="Departamento"]').value || null,
            'Pais': row.querySelector('input[name ="Pais"]').value || null,
            'ContactoID': row.querySelector('select[name="ContactoID"]').value || null,
            'Nacional': row.querySelector('select[name="Nacional"]').value,
        };

        let id = selected[0].value;
        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        fetch(`/clientes/editar/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al guardar los cambios');
            }
            return response.json();
        })
        .then(data => { 
            if (data.status == 'success') {
                showMessage('Cambios guardados correctamente.', 'success');
                window.location.reload()

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
    };

    async function handleDeleteConfirmation(event, modal, confirmButton, form, csrfToken) {
        event.preventDefault();
        const selectedIds = getSelectedIds();
        if (selectedIds.length == 0) {
            showMessage('No has seleccionado ningún cliente para eliminar.', 'danger');
            return;
        }

        modal.show();
        confirmButton.onclick = async function () {
            const relations = await verifyRelations(selectedIds, csrfToken);
            if (relations.isRelated) {
                let message = 'Algunos clientes no pueden ser eliminados porque están relacionados con las siguientes tablas:\n';
                for (const [id, tables] of Object.entries(relations.relaciones)) {
                    message += `Cliente ID ${id}: ${tables.join(', ')}\n`;
                }
                showMessage(message, 'danger', 5000); // Mostrar el mensaje por 5 segundos
                modal.hide();
                document.getElementById('select-all').checked = false;
                document.querySelectorAll('.row-select').forEach(checkbox => checkbox.checked = false);
                return;
            }

            document.getElementById('items_to_delete').value = selectedIds.join(',');
            form.submit();
        };
    }


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

            // Restaurar los valores originales desde el atributo personalizado
            row.querySelectorAll('select.form-control').forEach(select => {
                if (select.hasAttribute('data-original-value')) {
                    select.value = select.getAttribute('data-original-value');
                }
            });
            
            disableEditMode(selected,row);
            showMessage('Cambios cancelados.', 'danger');
        }
    };

    // Deshabilitar modo edición
    function disableEditMode(selected,row) {
        // Cambiar inputs a solo lectura
        row.querySelectorAll('input.form-control').forEach(input => {
            input.classList.add('form-control-plaintext');
            input.classList.remove('form-control');
            input.readOnly = true;
        });

        // Cambiar inputs a solo lectura
        row.querySelectorAll('select.form-control').forEach(selects => {
            selects.classList.add('form-control-plaintext');
            selects.classList.remove('form-control');
            selects.disabled = true;
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

    function getSelectedIds() {
        //return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
        const selectedIds = Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
        console.log(selectedIds); // Asegúrate de que los IDs son los correctos
        return selectedIds;
    }

    async function verifyRelations(ids, csrfToken) {
        try {
            const response = await fetch('/clientes/verificar-relaciones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ ids }),
            });


            if (!response.ok) {
                throw new Error('Error al verificar relaciones');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error verificando relaciones:', error);
            return { isRelated: true }; // Asumir que hay relaciones en caso de error
        }
    }
        

    function showMessage(message, type, duration = 6000) {
        const alertBox = document.getElementById('message-box');
        const alertIcon = document.getElementById('alert-icon');
        const alertMessage = document.getElementById('alert-message');

        alertMessage.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;

        const icons = {
            success: '✔️',
            danger: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        alertIcon.textContent = icons[type] || '';

        alertBox.style.display = 'block';
        setTimeout(() => {
            alertBox.classList.remove('show');
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 300);
        }, duration);
    }
});
