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

    // Obtener IDs seleccionados
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
        row.querySelectorAll('input.form-control-plaintext').forEach(input => {
            input.classList.remove('form-control-plaintext');
            input.classList.add('form-control');
            input.readOnly = false;
        });

        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    };

    // Deshabilitar modo edición
    function disableEditMode(selected, row) {
        // Cambiar inputs a solo lectura
        row.querySelectorAll('input.form-control').forEach(input => {
            input.classList.add('form-control-plaintext');
            input.classList.remove('form-control');
            input.readOnly = true;
        });

        selected.disabled = false;
        selected.checked = false;

        // Habilitar todos los checkboxes y el botón de edición
        document.getElementById('select-all').disabled = false;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = false);
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
                    row.querySelectorAll('input').forEach(input => {
                        input.classList.add('form-control-plaintext');
                        input.classList.remove('form-control');
                        input.readOnly = true;
                    });
                    showMessage('Concepto guardado con éxito.', 'success');
                    document.getElementById('save-button').classList.add('d-none');
                    disableEditMode(selected, row);
                } else {
                    showMessage('Error al guardar el concepto.', 'danger');
                }
            })
            .catch(error => {
                showMessage('Error en la comunicación con el servidor.', 'danger');
            });

        return false;
    };

});
