document.addEventListener('DOMContentLoaded', function () {
    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');
    const editButton = document.getElementById('edit-button');
    const cancelButton = document.getElementById('cancel-button');
    const deleteButton = document.getElementById('delete-button');
    const saveButton = document.getElementById('save-button');
    let originalValues = {};

    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function (event) {
        const checkboxes = document.querySelectorAll('.row-select');
        checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
    });

    // Manejar el botón de eliminación
    deleteButton.addEventListener('click', function (event) {
        try {
            event.preventDefault();
            const selectedIds = Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);

            if (selectedIds.length === 0) {
                alert('No has seleccionado ningún elemento para eliminar.');
                return;
            }

            document.getElementById('items_to_delete_eliminar').value = selectedIds.join(',');
            document.getElementById('delete-form').submit();
        } catch (error) {
            console.error('Error al eliminar:', error);
        }
    });

    document.querySelector('.btn-outline-danger.fas.fa-trash-alt').addEventListener('click', function (event) {
        event.preventDefault();
        const selectedIds = Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    
        if (selectedIds.length === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return;
        }
    
        document.getElementById('items_to_delete_eliminar').value = selectedIds.join(',');
        document.getElementById('delete-form').submit();
    });

    // ========== FUNCIÓN PARA DESCARGAR EXCEL ==========
    const downloadButton = document.querySelector('.btn-outline-info.fas.fa-download');
    const downloadForm = document.getElementById('download-form');

    downloadButton.addEventListener('click', function (event) {
        event.preventDefault(); // Evita el envío automático del formulario

        const selectedIds = Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);

        if (selectedIds.length === 0) {
            alert('¡Selecciona al menos un tipo de pagaré para descargar!');
            return;
        }

        // Asigna los IDs al input oculto del formulario de descarga
        document.getElementById('items_to_delete_descargar').value = selectedIds.join(',');
        downloadForm.submit(); // Envía el formulario
    });

    // ========== FUNCIONES GLOBALES ==========
    window.enableEdit = function () {
        const selected = document.querySelectorAll('.row-select:checked');
    
        if (selected.length !== 1) {
            alert('Selecciona solo un registro para editar.');
            return;
        }
    
        const row = selected[0].closest('tr');
        const span = row.querySelector('.descripcion-text');
        const input = row.querySelector('.descripcion-input');
    
        if (!input || !span) {
            alert('Error: No se encontró el campo de descripción.');
            return;
        }
    
        // Guarda el valor original antes de habilitar la edición
        originalValues[row.dataset.id] = input.value;
        console.log(`Guardando valor original: ${input.value}`);
    
        // Habilita la edición
        span.classList.add('d-none'); // Oculta el texto
        input.classList.remove('d-none'); // Muestra el input
        input.removeAttribute('readonly'); // Habilita la edición
    
        saveButton.classList.remove('d-none');
        cancelButton.classList.remove('d-none');
        editButton.disabled = true;
    };

    // Cancelar edición
    window.cancelEdit = function () {
        const selected = document.querySelectorAll('.row-select:checked');

        if (selected.length === 1) {
            const row = selected[0].closest('tr');
            const span = row.querySelector('.descripcion-text');
            const input = row.querySelector('.descripcion-input');

            if (!input || !span) {
                alert('Error: No se encontró el campo de descripción.');
                return;
            }

            // Restaura el valor original
            const originalValue = originalValues[row.dataset.id];
            if (originalValue !== undefined) {
                input.value = originalValue;
                span.textContent = originalValue;
                console.log(`Restaurando valor original: ${originalValue}`);
            } else {
                console.error('No se encontró el valor original para restaurar.');
            }

            input.classList.add('d-none'); // Oculta el input
            input.setAttribute('readonly', 'readonly'); // Deshabilita la edición
            span.classList.remove('d-none'); // Muestra el texto

            // Oculta los botones de "Guardar" y "Cancelar"
            document.getElementById('save-button').classList.add('d-none');
            document.getElementById('cancel-button').classList.add('d-none');

            // Habilita el botón de "Editar"
            document.getElementById('edit-button').disabled = false;

            // Limpia los valores originales
            delete originalValues[row.dataset.id];

            // Desmarca el checkbox
            selected[0].checked = false;
        }
    };

    // Guardar cambios
    window.saveRow = function () {
        const selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('Selecciona una fila para guardar.');
            return;
        }
    
        const row = selected.closest('tr');
        const span = row.querySelector('.descripcion-text');
        const input = row.querySelector('.descripcion-input');
    
        if (!input || !span) {
            alert('Error: No se encontró el campo de descripción.');
            return;
        }
    
        const nuevaDescripcion = input.value;
        const tipoPagareId = selected.value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
        console.log(`Guardando ID: ${tipoPagareId}, Descripción: ${nuevaDescripcion}`);
    
        fetch(`/TipoPagare/editar/${tipoPagareId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                Desc_Tipo_Pagare: nuevaDescripcion
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                span.textContent = nuevaDescripcion;
    
                input.classList.add('d-none');
                input.setAttribute('readonly', 'readonly');
                span.classList.remove('d-none');
    
                saveButton.classList.add('d-none');
                cancelButton.classList.add('d-none');
                editButton.disabled = false;
    
                delete originalValues[row.dataset.id];
    
                // Desmarca el checkbox
                selected.checked = false;
            } else {
                alert(`Error al guardar: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error en la solicitud fetch:', error);
            alert('Error de conexión.');
        });
    };

    // ========== FUNCIÓN DE MENSAJES ==========
    function showMessage(message, type) {
        const alertBox = document.getElementById('message-box');
        const alertMessage = document.getElementById('alert-message');

        alertMessage.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        alertBox.style.display = 'block';

        setTimeout(() => {
            alertBox.classList.remove('show');
            setTimeout(() => alertBox.style.display = 'none', 300);
        }, 3000);
    }
});