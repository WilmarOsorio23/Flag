document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Deshabilitar tecla Enter para prevenir envíos accidentales
    preventFormSubmissionOnEnter();

    // Modal de confirmación de eliminación
    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');

    // Botón seleccionar/deseleccionar todos
    document.getElementById('select-all').addEventListener('click', toggleCheckboxSelection);

    // Configuración de la confirmación de eliminación
    document.querySelector('.btn-outline-danger.fas.fa-trash-alt').addEventListener('click', function (event) {
        handleDeleteConfirmation(event, confirmDeleteModal, confirmDeleteButton, deleteForm, csrfToken);
    });

    // Evitar envío de formularios con Enter
    function preventFormSubmissionOnEnter() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        });
    }

    // Seleccionar/deseleccionar todos los checkboxes
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

    // Obtener IDs seleccionados
    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }

    // Verificar si los elementos seleccionados están relacionados con otros elementos en el backend
    async function verifyRelations(ids, csrfToken) {
        try {
            const response = await fetch('/verificar-relaciones/', {
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
        }, 800);
    }

    // Habilitar edición de conceptos
    window.enableEdit = function () {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            showMessage('No has seleccionado ningún concepto para editar.', 'danger');
            return false;
        }
        if (selected.length > 1) {
            showMessage('Solo puedes editar un concepto a la vez.', 'danger');
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
        inputs.forEach(input => {
            input.classList.remove('form-control-plaintext');
            input.classList.add('form-control');
            input.readOnly = false;
        });

        // Mostrar botones de "Guardar" y "Cancelar" en la parte superior
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    };

    // Deshabilitar modo edición
    function disableEditMode(selected, row) {
        // Cambiar inputs a solo lectura
        row.querySelectorAll('input').forEach(input => {
            if (input.classList.contains('form-control')) {  // Solo modificar los inputs editables
                input.classList.add('form-control-plaintext');
                input.classList.remove('form-control');
                input.readOnly = true;
            }
        });
        

        // Habilitar todos los checkboxes y el botón de edición
        document.getElementById('select-all').disabled = false;
        document.querySelectorAll('.row-select').forEach(checkbox => {
            checkbox.disabled = false;
            checkbox.checked = false;  // Desmarcar todos los checkboxes
        });
        document.getElementById('edit-button').disabled = false;

        // Ocultar los botones de guardar y cancelar
        document.getElementById('save-button').classList.add('d-none');
        document.getElementById('cancel-button').classList.add('d-none');
    }

    // Cancelar edición
    window.cancelEdit = function () {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length == 1) {

            let row = selected[0].closest('tr');

            // Restaurar los valores originales desde el atributo personalizado
            row.querySelectorAll('input.form-control').forEach(input => {
                if (input.hasAttribute('data-original-value')) {
                    input.value = input.getAttribute('data-original-value');
                }
            });

            selected.disabled = false;
            selected.checked = false;
            window.location.reload();
            disableEditMode(selected, row);
            showMessage('Cambios cancelados.', 'danger');
        }
    };

    // Confirmación antes de eliminar
    window.confirmDelete = function() {
        let selected = document.querySelectorAll('.row-select:checked').length;
        if (selected === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return false;
        }
        return confirm('¿Estás seguro de que deseas eliminar los elementos seleccionados?');
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

    // Guardar cambios del concepto
    window.saveRow = function () {
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            showMessage('No has seleccionado ningún concepto para guardar.', 'danger');
            return false;
        }

        let row = selected.closest('tr');
        let data = {
            'Descripcion': row.querySelector('input[name="Descripcion"]').value
        };

        let ConceptoId = selected.value;
        fetch(`/conceptos/editar/${ConceptoId}/`, {
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
                    // Ocultar botones de guardar y cancelar
                    document.getElementById('save-button').classList.add('d-none');
                    document.getElementById('cancel-button').classList.add('d-none');
                    
                    // Habilitar botón de edición
                    document.getElementById('edit-button').disabled = false;
                
                    row.querySelectorAll('input').forEach(input => {
                        input.classList.remove('form-control');
                        input.classList.add('form-control-plaintext');                        
                        input.readOnly = true;
                    });

                    // Habilitar y desmarcar checkboxes
                    document.getElementById('select-all').disabled = false;
                    document.querySelectorAll('.row-select').forEach(checkbox => {
                        checkbox.disabled = false;
                        checkbox.checked = false;
                    });

                    showMessage('Concepto guardado con éxito.', 'success');                                        
                } else {
                    showMessage('Error al guardar el concepto.', 'danger');
                }
            })
            .catch(error => {
                showMessage('Error en la comunicación con el servidor.', 'danger');
            });

        return false;
    };

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
    });
    
    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function (event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });
    
    const table = document.querySelector('.table-primary');
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
        
            rows.sort((a, b) => {
                const cellA = a.querySelector(`[data-field="${columnName}"]`);
                const cellB = b.querySelector(`[data-field="${columnName}"]`);
        
                if (!cellA || !cellB) return 0;
        
                // Obtener el texto o valor del elemento dentro de la celda
                const getCellValue = (cell) => {
                    const input = cell.querySelector('input');
                    const span = cell.querySelector('span');
                    const select = cell.querySelector('select');
                    if (input && !input.classList.contains('d-none')) {
                        return input.value.trim();
                    } else if (span) {
                        return span.innerText.trim();
                    } else if (select) {
                        return select.options[select.selectedIndex].text.trim();
                    }
                    return '';
                };
        
                const textA = getCellValue(cellA);
                const textB = getCellValue(cellB);
        
                // Numeric comparison
                if (!isNaN(textA) && !isNaN(textB)) {
                    return direction === 'asc' ? textA - textB : textB - textA;
                }
        
                // String comparison
                return direction === 'asc'
                    ? textA.localeCompare(textB)
                    : textB.localeCompare(textA);
            });
        
            rows.forEach(row => tbody.appendChild(row));
        }
    }

});
