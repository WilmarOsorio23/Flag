document.addEventListener('DOMContentLoaded', function() {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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
            const isRelated = await verifyRelations(selectedIds, csrfToken); // Verificar si hay relaciones con otros elementos
            if (isRelated) {
                showMessage('Algunos elementos no pueden ser eliminados porque están relacionados con otras tablas.', 'danger'); // Mensaje de error si hay relaciones
                modal.hide(); // Ocultar el modal
                document.getElementById('select-all').checked = false;
                document.querySelectorAll('.row-select').forEach(checkbox => checkbox.checked = false);
                return;
            }

            document.getElementById('items_to_delete').value = selectedIds.join(','); // Asignar los IDs seleccionados al formulario
            form.submit(); // Enviar el formulario para realizar la eliminación

        };
    }

    // Obtener los IDs de los elementos seleccionados (checkboxes marcados)
    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }

    // Verificar si los elementos seleccionados están relacionados con otros elementos en el backend
    async function verifyRelations(ids, csrfToken) {
        try {
            const response = await fetch('/consultores/verificar-relaciones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ ids }), // Enviar los IDs en el cuerpo de la solicitud
            });
            const data = await response.json(); // Obtener la respuesta como JSON
            console.log(data);
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
        }, 4000);
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

    // Habilitar edición en la fila seleccionada
    window.enableEdit = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length == 0) {
            showMessage('Por favor, selecciona al menos un consultor.', 'danger');
            return false;
        }
        if (selected.length > 1) {
            showMessage('Por favor, Selecciona un solo consultor para editar.', 'danger');
            return false;
        }

        let row = selected[0].closest('tr');
        let inputs = row.querySelectorAll('input.form-control-plaintext');
        let selects = row.querySelectorAll('select.form-control-plaintext');

        // Guardar valores originales en un atributo personalizado 
        inputs.forEach(input => { 
            input.setAttribute('data-original-value', input.value);
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

    window.saveRow = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length != 1) {
            showMessage('Error al guardar: No hay un consultor seleccionado.', 'danger');
            return;
        }

        let row = selected[0].closest('tbody tr');
        let id = selected[0].value;
        let data = {
            'TipoDocumentoID': row.querySelector('select[name="TipoDocumentoID"]').value,
            'Documento': row.querySelector('input[name="Documento"]').value,
            'Nombre': row.querySelector('input[name="Nombre"]').value,
            'Empresa': row.querySelector('input[name="Empresa"]').value,
            'Profesion': row.querySelector('input[name="Profesion"]').value,
            'LineaId': row.querySelector('select[name="LineaId"]').value,
            'ModuloId': row.querySelector('select[name="ModuloId"]').value,
            'PerfilId': row.querySelector('select[name="PerfilId"]').value,
            'Estado': row.querySelector('select[name="Estado"]').value,
            'Fecha_Ingreso': row.querySelector('input[name="Fecha_Ingreso"]').value || null,
            'Fecha_Retiro': row.querySelector('input[name="Fecha_Retiro"]').value || null,
            'Telefono': row.querySelector('input[name="Telefono"]').value || null,
            'Direccion': row.querySelector('input[name="Direccion"]').value || null,
            'Fecha_Operacion': row.querySelector('input[name="Fecha_Operacion"]').value || null,
            'Certificado': row.querySelector('select[name="Certificado"]').value,
            'Certificaciones': row.querySelector('input[name="Certificaciones"]').value || null,
            'Fecha_Nacimiento': row.querySelector('input[name="Fecha_Nacimiento"]').value || null,
            'Anio_Evaluacion': row.querySelector('input[name="Anio_Evaluacion"]').value || null,
            'NotaEvaluacion': row.querySelector('input[name="NotaEvaluacion"]').value || null
        };
        console.log(data);

        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        fetch(`/consultores/editar/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(JSON.stringify(errorData));
                });
            }
            return response.json();
        })
        
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
            let errorMessage = 'Error al guardar los cambios: ';
            try {
                let errorData = JSON.parse(error.message).error;
                for (let field in errorData) {
                    errorMessage += `${field}: ${errorData[field].join(', ')}. `;
                }
            } catch (e) {
                errorMessage += error.message;
            }
            showMessage(errorMessage.replace(/_/g, ' '), 'danger');
    
            // Restaurar los valores originales en caso de error
            row.querySelectorAll('input.form-control').forEach(input => {
                if (input.hasAttribute('data-original-value')) {
                    input.value = input.getAttribute('data-original-value');
                }
            });
    
            row.querySelectorAll('select.form-control').forEach(select => {
                if (select.hasAttribute('data-original-value')) {
                    select.value = select.getAttribute('data-original-value');
                }
            });
    
            disableEditMode(selected,row);
        });
    };
const table = document.getElementById('infoConsultoresTable');
if (table) {
    const headers = table.querySelectorAll('th.sortable');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-sort');
            const direction = header.getAttribute('data-direction') || 'asc';
            const newDirection = direction === 'asc' ? 'desc' : 'asc';

            sortTableByColumn(table, column, newDirection);

            // Reset all headers to default
            headers.forEach(h => {
                h.setAttribute('data-direction', 'default');
                h.querySelector('.sort-icon-default').style.display = 'inline';
                h.querySelector('.sort-icon-asc').style.display = 'none';
                h.querySelector('.sort-icon-desc').style.display = 'none';
            });
            
            // Set current header direction
            header.setAttribute('data-direction', newDirection);
            header.querySelector('.sort-icon-default').style.display = 'none';
            header.querySelector(`.sort-icon-${newDirection}`).style.display = 'inline';
        });
    });

    function sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Find column index by data-field attribute to be more precise
        const headerCells = Array.from(table.querySelectorAll('thead th'));
        const columnIndex = headerCells.findIndex(th => {
            return th.getAttribute('data-sort') === columnName;
        });
        
        if (columnIndex === -1) return; // Column not found

        rows.sort((a, b) => {
            // Find cells by data-field attribute for more reliable matching
            const cellA = a.querySelector(`td[data-field="${columnName}"]`);
            const cellB = b.querySelector(`td[data-field="${columnName}"]`);
            
            if (!cellA || !cellB) return 0;
            
            // Get the text content, handling different element types
            const getCellText = (cell) => {
                if (cell.querySelector('input, select')) {
                    return cell.querySelector('input, select').value.trim();
                }
                return cell.innerText.trim();
            };
            
            const textA = getCellText(cellA);
            const textB = getCellText(cellB);

            // Numeric comparison
            if (!isNaN(textA) && !isNaN(textB)) {
                return direction === 'asc' ? textA - textB : textB - textA;
            }

            // Date comparison
            if (columnName.includes('fecha') || columnName.includes('fecha')) {
                const dateA = new Date(textA);
                const dateB = new Date(textB);
                if (!isNaN(dateA) && !isNaN(dateB)) {
                    return direction === 'asc' ? dateA - dateB : dateB - dateA;
                }
            }

            // String comparison
            return direction === 'asc' 
                ? textA.localeCompare(textB) 
                : textB.localeCompare(textA);
        });

        // Reattach sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
}
});
