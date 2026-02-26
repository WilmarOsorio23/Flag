document.addEventListener('DOMContentLoaded', function() {
    
    // Clonar checkboxes seleccionados en el formulario de descarga
    document.getElementById('download-form').addEventListener('submit', function(event) {
    let selectedCheckboxes = document.querySelectorAll('.row-select:checked');
    if (selectedCheckboxes.length === 0) {
        alert('No has seleccionado ningún elemento para descargar.');
        event.preventDefault(); // Evita el envío si no hay elementos seleccionados
        return;
    }

    // Captura los valores de los checkboxes seleccionados
    let selectedValues = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
     // Asigna los valores seleccionados al campo oculto
     document.getElementById('items_to_download').value = selectedValues.join(',');
   });

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    window.saveRow = function() {
        
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length != 1) {
            showMessage('Error al guardar: No hay un detalle seleccionado.', 'danger');
            return;
        }

        let row = selected[0].closest('tr');

        // Obtener el valor del campo NumeroOtroSi
        let numeroOtroSi = row.querySelector('input[name="NumeroOtroSi"]').value.trim();


        if (!numeroOtroSi) {
            showMessage('El campo Número Otro Sí no puede estar vacío.', 'danger');
            return;
        }
       
        let data = {
            'FechaFin': row.querySelector('input[name="FechaFin"]').value || null, 
            'NumeroOtroSi': row.querySelector('input[name="NumeroOtroSi"]').value,
            'ValorOtroSi': row.querySelector('input[name="ValorOtroSi"]').value || null,
            'ValorIncluyeIva': row.querySelector('input[name="ValorIncluyeIva"]').checked,
            'Polizas': row.querySelector('input[name="Polizas"]').checked,
            'PolizasDesc': row.querySelector('input[name="PolizasDesc"]').value,
            'FirmadoFlag': row.querySelector('input[name="FirmadoFlag"]').checked,
            'FirmadoCliente': row.querySelector('input[name="FirmadoCliente"]').checked,
            'monedaId': row.querySelector('select[name="moneda"]').value,
            'Contrato': row.querySelector('select[name="Contrato"]').value,
        };
        
        let id = selected[0].value;
        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

       fetch(`/contratos_otros_si/editar/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Error desconocido');
                });
            }
            return response.json();
        })
        .then(data => { 
            if (data.status == 'success') {
                showMessage('Cambios guardados correctamente.', 'success');
                    window.location.reload()

                row.querySelectorAll('input.form-control').forEach(input => {
                    input.classList.add('highlighted');
                    setTimeout(() => input.classList.remove('highlighted'), 5000);
                });

                disableEditMode(selected,row);

            } else {
                window.location.reload()
                showMessage('Error al guardar los cambios: ' + (data.error || 'Error desconocido'), 'danger')
            }
            
        })
        .catch(error => {
            console.error('Error al guardar los cambios:', error);
            showMessage(error.message, 'danger'); // Muestra el mensaje de error específico
        });
    };

    window.enableEdit = function () {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún registro para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un registro a la vez.');
            return false;
        }

        const row = selected[0].closest('tr');

        // Lista de campos específicos que son editables
        const editableFields = [
            { name: "FechaFin", type: "date" },
            { name: "NumeroOtroSi", type: "text" },
            { name: "ValorOtroSi", type: "text" },
            { name: "ValorIncluyeIva", type: "checkbox" },
            { name: "Polizas", type: "checkbox" },
            { name: "PolizasDesc", type: "text" },
            { name: "FirmadoFlag", type: "checkbox" },
            { name: "FirmadoCliente", type: "checkbox" },
            { name: "moneda", type: "select" },
            { name: "Contrato", type: "select" }
        ];

        // Guardar valores originales en un atributo personalizado
        editableFields.forEach(field => {
            const element = row.querySelector(`[name="${field.name}"]`);
            const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
            if (element) {
                if (field.type === "checkbox") {
                    element.setAttribute('data-original-value', element.checked);
                } else {
                    element.setAttribute('data-original-value', element.value);
                }
            }
            if (span) {
                span.setAttribute('data-original-value', span.innerText.trim());
            }
        });

        // Habilitar los campos editables y ocultar los spans correspondientes
        editableFields.forEach(field => {
            const element = row.querySelector(`[name="${field.name}"]`);
            const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
            if (element) {
                if (field.type === "checkbox") {
                    const display = row.querySelector(`.boolean-display[data-field="${field.name}"]`);
                    const checkbox = row.querySelector(`.boolean-edit[name="${field.name}"]`);
                    if (display && checkbox) {
                        display.classList.add('d-none'); // Ocultar texto en modo edición
                        checkbox.classList.remove('d-none'); // Mostrar checkbox en modo edición
                    }
                } else if (field.type === "select") {
                    element.disabled = false; // Habilitar el select en modo edición
                    element.classList.remove('form-control-plaintext'); // Quitar estilo de solo lectura
                    element.classList.add('form-control'); // Agregar estilo editable
                } else {
                    element.classList.remove('d-none'); // Mostrar el input
                    element.classList.add('form-control');
                    element.readOnly = false;
                }
            }
            if (span) {
                span.classList.add('d-none'); // Ocultar el span en modo edición
            }
        });

        // Desactivar todos los checkboxes y botones de edición
        document.getElementById('select-all').disabled = true;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        // Mostrar botones de "Guardar" y "Cancelar"
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    };


    window.cancelEdit = function () {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 1) {
            const row = selected[0].closest('tr');

            // Restaurar valores originales
            const editableFields = [
                "FechaFin", "NumeroOtroSi", "ValorOtroSi", "ValorIncluyeIva",
                "Polizas", "PolizasDesc", "FirmadoFlag", "FirmadoCliente",
                "moneda", "Contrato"
            ];

            editableFields.forEach(name => {
                const element = row.querySelector(`[name="${name}"]`);
                const span = row.querySelector(`[data-field="${name}"] span.form-control-plaintext`);
                if (element) {
                    if (element.type === "checkbox") {
                        element.checked = element.getAttribute('data-original-value') === "true";
                    } else {
                        element.value = element.getAttribute('data-original-value');
                    }
                }
                if (span) {
                    span.innerText = span.getAttribute('data-original-value');
                }
            });

            // Deshabilitar los campos y restaurar el modo de solo lectura
            editableFields.forEach(name => {
                const element = row.querySelector(`[name="${name}"]`);
                const span = row.querySelector(`[data-field="${name}"] span.form-control-plaintext`);
                if (element) {
                    if (element.type === "checkbox") {
                        const display = row.querySelector(`.boolean-display[data-field="${name}"]`);
                        const checkbox = row.querySelector(`.boolean-edit[name="${name}"]`);
                        if (display && checkbox) {
                            display.classList.remove('d-none'); // Mostrar texto en modo solo lectura
                            checkbox.classList.add('d-none'); // Ocultar checkbox en modo solo lectura
                        }
                    } else if (element.tagName === "SELECT") {
                        element.disabled = true;
                        element.classList.add('form-control-plaintext');
                        element.classList.remove('form-control');
                    } else {
                        element.classList.add('d-none'); // Ocultar el input
                        element.classList.remove('form-control');
                        element.readOnly = true;
                    }
                }
                if (span) {
                    span.classList.remove('d-none'); // Mostrar el span en modo solo lectura
                }
            });

            // Restaurar botones y checkboxes
            document.getElementById('select-all').disabled = false;
            document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = false);
            document.getElementById('edit-button').disabled = false;

            // Ocultar botones de "Guardar" y "Cancelar"
            document.getElementById('save-button').classList.add('d-none');
            document.getElementById('cancel-button').classList.add('d-none');
        }
    };

    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Inicialización del modal de confirmación y botón de confirmación de eliminación
    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');

    // Asociar el evento de clic al botón de seleccionar/deseleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', toggleCheckboxSelection);

    // Configurar el evento de clic para el botón de eliminación
    document.querySelector('.btn-outline-danger.fas.fa-trash-alt').addEventListener('click', function (event) {
        handleDeleteConfirmation(event, confirmDeleteModal, confirmDeleteButton, deleteForm, csrfToken);
    });
    
 
    // Funciones reutilizables

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

    // Alternar la selección de todos los checkboxes al hacer clic en el checkbox "Seleccionar todo"
    function toggleCheckboxSelection(event) {
        const checkboxes = document.querySelectorAll('.row-select');
        checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
    }

     // Obtener los IDs de los elementos seleccionados (checkboxes marcados)
     function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }

    // Manejar la confirmación de eliminación
    async function handleDeleteConfirmation(event, modal, confirmButton, form, csrfToken) {
        event.preventDefault(); // Prevenir la acción predeterminada del evento
        const selectedIds = getSelectedIds(); // Obtener los IDs de los elementos seleccionados
        if (selectedIds.length == 0) {
            showMessage('No has seleccionado ningún elemento para eliminar.', 'danger'); // Mostrar mensaje si no hay elementos seleccionados
            return;
        }

        modal.show(); // Mostrar el modal de confirmación de eliminación

        confirmButton.onclick = async function () {
            const itemsToDelete = document.getElementById('items_to_delete');
            if (itemsToDelete) {
                itemsToDelete.value = selectedIds.join(',');
            } else {
                console.error("El elemento con ID 'items_to_delete' no se encuentra en el DOM.");
            }
                   
            form.submit(); // Enviar el formulario para realizar la eliminación

        };
    }

    // Verificar si los elementos seleccionados están relacionados con otros elementos en el backend
    async function verifyRelations(ids, csrfToken) {
        try {
            const response = await fetch('verificar-relaciones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ ids }), // Enviar los IDs en el cuerpo de la solicitud
            });
            const data = await response.json(); // Obtener la respuesta como JSON
            return data.isRelated || false; // Si la respuesta indica que están relacionados, retornar true
        } catch (error) {
            console.error('Error verificando relaciones:', error);
            return true; // Asumir que están relacionados en caso de error
        }
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
        }, 5000);
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


    // Deshabilitar modo edición
    function disableEditMode(selected,row) {
        // Cambiar inputs a solo lectura
        row.querySelectorAll('input.form-control').forEach(input => {
            input.classList.add('form-control-plaintext');
            input.classList.remove('form-control');
            input.readOnly = true;
        });

        // Deshabilitar el campo select
        row.querySelectorAll('select').forEach(select => {
            select.disabled = true; // Deshabilitar el select
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

});