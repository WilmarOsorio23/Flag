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

        selectedCheckboxes.forEach(function (checkbox) {
            let clonedCheckbox = checkbox.cloneNode();
            clonedCheckbox.setAttribute('type', 'hidden'); // Ocultarlo en el formulario
            document.getElementById('download-form').appendChild(clonedCheckbox);
        });
    });

    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function (event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
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

    window.enableEdit = function() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún Cliente para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un Cliente a la vez.');
            return false;
        }
    
        let row = selected[0].closest('tr'); // Asegura que se obtiene la fila correcta
        let inputs = row.querySelectorAll('input.form-control-plaintext'); // Asegura que el selector sea correcto
    
        inputs.forEach(input => {
            input.classList.remove('form-control-plaintext'); // Cambiar la clase
            input.classList.add('form-control');
            input.readOnly = false; // Hacerlo editable
        });
    
        // Mostrar botón de guardar
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    };
    

    // Guardar los cambios en la fila seleccionada
    window.saveRow = function () {
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ningún Cliente para guardar.');
            return false;
        }

        let row = selected.closest('tr');
        let data = {
            'Nombre_Cliente': row.querySelector('input[name ="Nombre_Cliente"]').value,
            'Activo': row.querySelector('input[name ="Activo"]').checked,
            'Fecha_Inicio': row.querySelector('input[name ="Fecha_Inicio"]').value,
            'Fecha_Retiro': row.querySelector('input[name ="Fecha_Retiro"]').value,
        };

        console.log(data)
        let ClienteId = selected.value;
        console.log(ClienteId)

        fetch(`/clientes/editar/${ClienteId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}', // Asegura que sea dinámico y no del backend
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    //inputs.forEach(input => {
                    row.querySelectorAll('input').forEach(input => {
                        input.classList.add('form-control-plaintext');
                        input.classList.remove('form-control');
                        input.readOnly = true;
                    });
                    document.getElementById('save-button').classList.add('d-none');
                } else {
                    alert('Error al guardar los cambios: ' + JSON.stringify(data.errors));
                }
            })
            .catch(error => {
                alert('Error al enviar los datos: ' + error.message);
            });

        return false;
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
            const isRelated = await verifyRelations(selectedIds, csrfToken);
            if (isRelated) {
                showMessage('Algunos clientes no pueden ser eliminados porque están relacionados con otras tablas.', 'danger');
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
            
            disableEditMode(selected,row);
            showMessage('Cambios cancelados.', 'danger');
        }
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

    function getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
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
            const data = await response.json();
            return data.isRelated || false;
        } catch (error) {
            console.error('Error verificando relaciones:', error);
            return true;
        }
    }

    function showMessage(message, type) {
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
        }, 800);
    }

});
