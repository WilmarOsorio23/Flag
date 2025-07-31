document.addEventListener('DOMContentLoaded', function() {
    

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

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    window.saveRow = function() {
        
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length != 1) {
            showMessage('Error al guardar: No hay un detalle seleccionado.', 'danger');
            return;
        }

        let row = selected[0].closest('tr');
       
        let data = {
            'valorHora': row.querySelector('input[name="valorHora"]').value,
            'valorDia': row.querySelector('input[name="valorDia"]').value,
            'valorMes': row.querySelector('input[name="valorMes"]').value,
            'monedaId': row.querySelector('select[name="moneda"]').value,
            'moduloId': row.querySelector('select[name="moduloId"]').value,
            'iva': row.querySelector('input[name="iva"]').value.trim() || null,
            'rteFte': row.querySelector('input[name="rteFte"]').value.trim() || null,
        };

        let idd = selected[0].value;
        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

       console.log(idd)
       console.log(data)
       fetch(`/tarifa_consultores/editar/${idd}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
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
                restoreOriginalValues(row); // Restaurar valores originales en caso de error
            }

        })
        .catch(error => {
            console.error('Error al guardar los cambios:', error);
            showMessage('Error al guardar los cambios: ' + error.message, 'danger');
            restoreOriginalValues(row); // Restaurar valores originales en caso de error

            disableEditMode(selected,row);
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
            { name: "rteFte", type: "text" },
            { name: "valorHora", type: "text" },
            { name: "valorDia", type: "text" },
            { name: "valorMes", type: "text" },
            { name: "moduloId", type: "select" },
            { name: "iva", type: "text" },
            { name: "moneda", type: "select" }
        ];

        // Guardar valores originales en un atributo personalizado
        editableFields.forEach(field => {
            const element = row.querySelector(`[name="${field.name}"]`);
            const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
            if (element) {
                element.setAttribute('data-original-value', element.value);
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
                if (field.type === "select") {
                    element.disabled = false; // Habilitar el select
                    element.classList.remove('form-control-plaintext');
                    element.classList.remove('d-none'); // Mostrar el select si estaba oculto
                    element.classList.add('form-control');
                } else {
                    element.classList.remove('d-none'); // Mostrar el input
                    element.classList.remove('form-control-plaintext');
                    element.classList.add('form-control');
                    element.readOnly = false; // Habilitar el input
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
                "valorHora", "valorDia", "valorMes", "rteFte",
                "iva", "moneda", "moduloId"
            ];

            editableFields.forEach(name => {
                const element = row.querySelector(`[name="${name}"]`);
                const span = row.querySelector(`[data-field="${name}"] span.form-control-plaintext`);
                if (element) {
                    if (element.tagName === "SELECT") {
                        element.value = element.getAttribute('data-original-value');
                        element.disabled = true; // Deshabilitar el select
                        element.classList.add('form-control-plaintext');
                        element.classList.remove('form-control');
                        element.classList.add('d-none'); // Ocultar el select
                    } else {
                        element.value = element.getAttribute('data-original-value');
                        element.classList.add('form-control-plaintext');
                        element.classList.remove('form-control');
                        element.readOnly = true;
                        element.classList.add('d-none'); // Ocultar el input
                    }
                }
                if (span) {
                    span.innerText = span.getAttribute('data-original-value');
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
        console.log("si esta entrando en handledelete")
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
        }, 800);
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

        // Cambiar selects a solo lectura
        row.querySelectorAll('select').forEach(select => {
            select.disabled = true;
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

    function restoreOriginalValues(row) {
        row.querySelectorAll('input.form-control').forEach(input => {
            if (input.hasAttribute('data-original-value')) {
                input.value = input.getAttribute('data-original-value'); // Restaurar valor original
            }
        });
    
        row.querySelectorAll('select.form-control').forEach(select => {
            if (select.hasAttribute('data-original-value')) {
                select.value = select.getAttribute('data-original-value'); // Restaurar valor original
            }
        });
    }
   
    
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