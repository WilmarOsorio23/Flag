document.addEventListener('DOMContentLoaded', function () {
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
        handleDeleteConfirmation(event, confirmDeleteModal, confirmDeleteButton, deleteForm);
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

    // Confirmar eliminación
    async function handleDeleteConfirmation(event, modal, confirmButton, form) {
        event.preventDefault();
        const selectedIds = getSelectedIds();
        if (selectedIds.length === 0) {
            showMessage('No has seleccionado ningún concepto para eliminar.', 'danger');
            return;
        }
        modal.show();

        confirmButton.onclick = async function () {
            document.getElementById('items_to_delete').value = selectedIds.join(',');
            form.submit();
        };
    }

    // Obtener IDs seleccionados
    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }

    // Mostrar mensajes en la interfaz
    function showMessage(message, type) {
        const alertBox = document.getElementById('message-box');
        alertBox.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
                                ${message}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                              </div>`;
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

    // Cancelar edición
    window.cancelEdit = function () {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 1) {
            let row = selected[0].closest('tr');
            row.querySelectorAll('input.form-control').forEach(input => {
                input.classList.add('form-control-plaintext');
                input.classList.remove('form-control');
                input.readOnly = true;
            });
            showMessage('Edición cancelada.', 'info');
        }
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
