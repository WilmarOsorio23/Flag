document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Recuperar los valores de año y mes originales desde la URL y almacenarlos en localStorage
    updateAnioMesFromURL();

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Funciones reutilizables

    // Actualizar los valores de año y mes desde la URL y mostrarlos en la interfaz
    function updateAnioMesFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const anio = urlParams.get('Anio');
        const mes = urlParams.get('Mes');
        const cliente = urlParams.get('ClienteId');
        if (anio && mes) {
            document.querySelector('#anio-original').textContent = anio;
            document.querySelector('#mes-original').textContent = mes;
            // Guardar los valores en variables globales
            window.originalAnio = anio;
            window.originalMes = mes;
            window.originalCliente = cliente;
            // Activar el botón de guardar si hay año y mes
            document.getElementById('save-button').removeAttribute('disabled');
            // Activar el botón de agregar línea si hay año, mes y cliente
            if (cliente) {
                document.getElementById('add-line').removeAttribute('disabled');
            }
        }
    }

    // Prevenir el envío del formulario al presionar la tecla Enter
    function preventFormSubmissionOnEnter() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', function (event) {
                if (event.key === "Enter") {
                    event.preventDefault(); // Prevenir la acción predeterminada de la tecla Enter
                }
            });
        });
    }

    // Mostrar mensajes de alerta
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

    // Función para guardar todas las filas
    function saveAllRows() {
        const rows = document.querySelectorAll('tbody tr');
        const data = [];

        rows.forEach((row, index) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');
            const selects = row.querySelectorAll('select');

            // Recopilar todos los valores de los inputs en la fila
            inputs.forEach(input => {
                if (input.name) {
                    rowData[input.name] = input.value || null;
                }
            });

            // Añadir el id de la fila
            const rowId = row.getAttribute('id');
            if (rowId) {
                rowData['ConsecutivoId'] = rowId.replace('row-', '');
            }

            // Añadir los datos adicionales
            rowData['Anio'] = window.originalAnio;
            rowData['Mes'] = window.originalMes;

            // Verificar si los datos ingresados por el usuario son válidos
            const userInputs = ['Horas', 'Dias', 'Meses', 'Valor', 'Descripcion', 'Numero_Factura'];
            const hasValidUserData = userInputs.some(field => rowData[field] !== null && rowData[field] !== '' && rowData[field] !== '0');

            // Verificar si la fila tiene datos válidos antes de añadirla
            if (hasValidUserData && rowData['ClienteId'] && rowData['LineaId']) {
                data.push(rowData);
            }
        });

        console.log(data);
        showSavingMessage(true);

        // Realizar la petición para guardar los datos
        fetch('/clientes_factura/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ data: data })
        })
        .then(response => response.json())
        .then(result => {
            showSavingMessage(false);
            if (result.status === 'success') {
                showMessage('Datos guardados correctamente.', 'success');
                // Deshabilitar o eliminar el botón de eliminar línea después de guardar
                document.querySelectorAll('tbody tr').forEach(row => {
                    const deleteButton = row.querySelector('button[aria-label="Close"]');
                    if (deleteButton) {
                        deleteButton.remove(); // Eliminar el botón
                    }
                });
            } else {
                showMessage('Error al guardar los datos.', 'danger');
            }
        })
        .catch(error => {
            showSavingMessage(false);
            console.error('Error:', error);
            showMessage('Error de conexión al guardar los datos.', 'danger');
        });
    }

    function showSavingMessage(show) {
        const savingMessage = document.getElementById('saving-message');
        if (show) {
            savingMessage.style.display = 'block';
        } else {
            savingMessage.style.display = 'none';
        }
    }

    function recalculateTotals() {
        const rows = document.querySelectorAll('tbody tr');
        const totals = {
            totalHoras: 0,
            totalDias: 0,
            totalValor: 0
        };

        rows.forEach(row => {
            let horasInput = row.querySelector('input[name="Horas"]');
            let diasInput = row.querySelector('input[name="Dias"]');
            let valorInput = row.querySelector('input[name="Valor"]');
            
            let horas = horasInput ? parseFloat(horasInput.value) : 0;
            let dias = diasInput ? parseFloat(diasInput.value) : 0;
            let valor = valorInput ? parseFloat(valorInput.value) : 0;

            // Verificar si los valores son números válidos
            if (isNaN(horas)) horas = 0;
            if (isNaN(dias)) dias = 0;
            if (isNaN(valor)) valor = 0;

            totals.totalHoras += horas;
            totals.totalDias += dias;
            totals.totalValor += valor;
        });

        // Actualizar los totales en el pie de página
        document.querySelector('tfoot th[data-total-horas]').textContent = totals.totalHoras.toFixed(0);
        document.querySelector('tfoot th[data-total-dias]').textContent = totals.totalDias.toFixed(0);
        document.querySelector('tfoot th[data-total-valor]').textContent = totals.totalValor.toFixed(0);
    }

    document.querySelectorAll('input[name="Horas"], input[name="Dias"], input[name="Valor"]').forEach(input => {
        input.addEventListener('input', recalculateTotals);
    });

    // Función para confirmar la adición de una nueva línea
    function confirmAddLine() {
        const lineaId = document.querySelector('select[name="LineaIdModal"]').value;
        const clienteId = window.originalCliente;
        const tbody = document.querySelector('tbody');


        if (!lineaId) {
            showMessage('Seleccione una línea.', 'warning');
            return;
        }

        // Crear una nueva fila en la tabla
        const newRow = document.createElement('tr');
        newRow.setAttribute('id', `row-`);
        newRow.innerHTML = `
            <td>
                <button type="button" class="btn btn-danger fas fa-times" aria-label="Close" onclick="removeLine(this)"></button>
                <input type="text" name="ClienteId" class="form-control" value="${clienteId}" hidden>
            </td>
            <td>${document.querySelector('select[name="LineaIdModal"] option:checked').textContent}
                <input type="text" name="LineaId" class="form-control" value="${lineaId}" hidden>
            </td>
            <td><input type="text" name="Horas" class="form-control" value=""></td>
            <td><input type="text" name="Dias" class="form-control" value=""></td>
            <td><input type="text" name="Meses" class="form-control" value=""></td>
            <td><input type="text" name="Valor" class="form-control" value=""></td>
            <td><input type="text" name="Descripcion" class="form-control" value=""></td>
            <td><input type="text" name="Numero_Factura" class="form-control" value=""></td>
        `;
        tbody.appendChild(newRow);

        // Ocultar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addLineModal'));
        modal.hide();
    }

    // Función para eliminar una línea
    function removeLine(button) {
        const row = button.closest('tr');
        row.remove();
        recalculateTotals();
    }

    // Habilitar o deshabilitar los botones según los filtros aplicados
    function toggleButtons() {
        const anio = document.querySelector('select[name="Anio"]').value;
        const mes = document.querySelector('select[name="Mes"]').value;
        const cliente = document.querySelector('select[name="ClienteId"]').value;
        const saveButton = document.getElementById('save-button');
        const addLineButton = document.getElementById('add-line');

        if (anio && mes && window.searchPerformed) {
            saveButton.removeAttribute('disabled');
        } else {
            saveButton.setAttribute('disabled', 'disabled');
        }

        if (anio && mes && cliente && window.searchPerformed) {
            addLineButton.removeAttribute('disabled');
        } else {
            addLineButton.setAttribute('disabled', 'disabled');
        }
    }


    // Añadir evento para habilitar o deshabilitar los botones
    document.querySelector('select[name="Anio"]').addEventListener('change', toggleButtons);
    document.querySelector('select[name="Mes"]').addEventListener('change', toggleButtons);
    document.querySelector('select[name="ClienteId"]').addEventListener('change', toggleButtons);

    // Marcar que se ha realizado una búsqueda
    document.querySelector('form').addEventListener('submit', function () {
        window.searchPerformed = true;
        toggleButtons(); // Re-evaluar los botones después de la búsqueda
    });

    window.saveAllRows = saveAllRows;
    window.confirmAddLine = confirmAddLine;
    window.removeLine = removeLine;
    recalculateTotals(); // Initial calculation
});