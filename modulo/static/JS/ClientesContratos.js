document.addEventListener('DOMContentLoaded', function() {
    
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
            selected.disabled = false;
            selected.checked = false;
            window.location.reload();
            disableEditMode(selected,row);
            showMessage('Cambios cancelados.', 'danger');
        }
    };

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
       
        let data = {
            'FechaFin': row.querySelector('input[name="FechaFin"]').value || null,  // Permitir valor nulo
            'Contrato': row.querySelector('input[name="Contrato"]').value,
            'ContratoVigente': row.querySelector('input[name="ContratoVigente"]').checked,
            'OC_Facturar': row.querySelector('input[name="OC_Facturar"]').checked,
            'Parafiscales': row.querySelector('input[name="Parafiscales"]').checked,
            'HorarioServicio': row.querySelector('input[name="HorarioServicio"]').value,
            'FechaFacturacion': row.querySelector('input[name="FechaFacturacion"]').value,
            'TipoFacturacion': row.querySelector('input[name="TipoFacturacion"]').value,
            'Observaciones': row.querySelector('input[name="Observaciones"]').value,
            'Polizas': row.querySelector('input[name="Polizas"]').checked,
            'PolizasDesc': row.querySelector('input[name="PolizasDesc"]').value,
            'ContratoValor': row.querySelector('input[name="ContratoValor"]').value || null,  // Permitir valor nulo
            'IncluyeIvaValor': row.querySelector('input[name="IncluyeIvaValor"]').checked,
            'ContratoDesc': row.querySelector('input[name="ContratoDesc"]').value,
            'ServicioRemoto': row.querySelector('input[name="ServicioRemoto"]').checked,
            'monedaId': row.querySelector('select[name="moneda"]').value,
        };
        
        let id = selected[0].value;
        // Deshabilitar los checkboxes y el botón de edición
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

       fetch(`/clientes_contratos/editar/${id}/`, {
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
                window.location.reload()
                showMessage('Error al guardar los cambios: ' + (data.error || 'Error desconocido'), 'danger')
            }
            
        })
        .catch(error => {
            console.error('Error al guardar los cambios:', error);
            showMessage('Error al guardar los cambios: ' + error.message, 'danger');

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
            { name: "FechaFin", type: "date" },
            { name: "Contrato", type: "text" },
            { name: "ContratoVigente", type: "checkbox" },
            { name: "OC_Facturar", type: "checkbox" },
            { name: "Parafiscales", type: "checkbox" },
            { name: "HorarioServicio", type: "text" },
            { name: "FechaFacturacion", type: "text" },
            { name: "TipoFacturacion", type: "text" },
            { name: "Observaciones", type: "text" }, // Aseguramos que Observaciones esté incluido
            { name: "Polizas", type: "checkbox" },
            { name: "PolizasDesc", type: "text" },
            { name: "ContratoValor", type: "text" },
            { name: "IncluyeIvaValor", type: "checkbox" },
            { name: "ContratoDesc", type: "text" },
            { name: "ServicioRemoto", type: "checkbox" },
            { name: "moneda", type: "select" },
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
                "FechaFin", "Contrato", "ContratoVigente", "OC_Facturar", "Parafiscales",
                "HorarioServicio", "FechaFacturacion", "TipoFacturacion", "Observaciones",
                "Polizas", "PolizasDesc", "ContratoValor", "IncluyeIvaValor",
                "ContratoDesc", "ServicioRemoto", "moneda"
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

    document.getElementById('select-all').addEventListener('click', function(event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });

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

   

    // Verificar si los elementos seleccionados están relacionados con otros elementos en el backend
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

    function showMessage(message, type, duration = 3000) {
        const alertBox = document.getElementById('message-box');
        const alertIcon = document.getElementById('alert-icon');
        const alertMessage = document.getElementById('alert-message');
  

        // Asignar el mensaje y el tipo de alerta
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