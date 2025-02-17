document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Recuperar los valores de año y mes originales desde la URL y almacenarlos en localStorage
    updateAnioMesFromURL();

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Funciones reutilizables

    function updateAnioMesFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const anio = urlParams.get('Anio');
        const mes = urlParams.get('Mes');
        const cliente = urlParams.get('ClienteId');
        if (anio && mes) {
            document.querySelector('#anio-original').textContent = anio;
            document.querySelector('#mes-original').textContent = mes;
            window.originalAnio = anio;
            window.originalMes = mes;
            window.originalCliente = cliente;
            // Si en sessionStorage se marcó que ya se realizó la búsqueda, lo establecemos
            if (sessionStorage.getItem('searchPerformed') === 'true') {
                window.searchPerformed = true;
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
            const userInputs = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa', 'Valor', 'Descripcion', 'Numero_Factura', 'IVA', 'Referencia', 'Ceco', 'Sitio_Serv'];
            const hasValidUserData = userInputs.some(field => rowData[field] !== null && rowData[field] !== '' && rowData[field] !== '0');

            // Verificar si la fila tiene datos válidos antes de añadirla
            if (hasValidUserData && rowData['ClienteId'] && rowData['LineaId']) {
                data.push(rowData);
            }
        });

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

    function updateRowTotal(row) {
        const horas = parseFloat(row.querySelector('input[name="Horas"]').value) || 0;
        const valorHoras = parseFloat(row.querySelector('input[name="Valor_Horas"]').value) || 0;
        const dias = parseFloat(row.querySelector('input[name="Dias"]').value) || 0;
        const valorDias = parseFloat(row.querySelector('input[name="Valor_Dias"]').value) || 0;
        const meses = parseFloat(row.querySelector('input[name="Meses"]').value) || 0;
        const valorMeses = parseFloat(row.querySelector('input[name="Valor_Meses"]').value) || 0;
        
        const total = (horas * valorHoras) + (dias * valorDias) + (meses * valorMeses);
        row.querySelector('input[name="Valor"]').value = total.toFixed(2);
    }    

    function recalculateTotals() {
        const rows = document.querySelectorAll('tbody tr');
        const totals = {
            totalHoras: 0,
            totalDias: 0,
            totalValor: 0
        };
    
        rows.forEach(row => {
            // Actualizar total de la fila primero
            updateRowTotal(row);
            
            // Sumar a los totales generales
            const horas = parseFloat(row.querySelector('input[name="Horas"]').value) || 0;
            const dias = parseFloat(row.querySelector('input[name="Dias"]').value) || 0;
            const valor = parseFloat(row.querySelector('input[name="Valor"]').value) || 0;
    
            totals.totalHoras += horas;
            totals.totalDias += dias;
            totals.totalValor += valor;
        });
    
        // Actualizar los totales en el pie de página
        document.querySelector('tfoot th[data-total-horas]').textContent = totals.totalHoras.toFixed(0);
        document.querySelector('tfoot th[data-total-dias]').textContent = totals.totalDias.toFixed(0);
        document.querySelector('tfoot th[data-total-valor]').textContent = totals.totalValor.toFixed(2);
    }

    // Modificar los event listeners para incluir todos los campos relevantes
    document.querySelectorAll('input[name="Horas"], input[name="Valor_Horas"], input[name="Dias"], input[name="Valor_Dias"], input[name="Meses"], input[name="Valor_Meses"]').forEach(input => {
        input.addEventListener('input', () => {
            // Actualizar la fila actual y luego los totales generales
            updateRowTotal(input.closest('tr'));
            recalculateTotals();
        });
    });

    function confirmAddLine() {
        const lineaId = document.querySelector('select[name="LineaIdModal"]').value;
        const clienteId = window.originalCliente;
        const anio = window.originalAnio; // Obtener el año del filtro
        const mes = window.originalMes;   // Obtener el mes del filtro
    
        if (!lineaId) {
            showMessage('Seleccione una línea.', 'warning');
            return;
        }

        // Mostrar el mensaje de "Agregando..."
        const addingMessage = document.getElementById('adding-message');
        addingMessage.style.display = 'block';
    
        // Obtener la tarifa asociada al cliente y la línea
        fetch(`/clientes_factura/obtener_factura/?clienteId=${clienteId}&lineaId=${lineaId}&anio=${anio}&mes=${mes}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response.json();
        })
        .then(tarifa => {
            const tbody = document.querySelector('tbody');
    
            // Crear una nueva fila en la tabla con los valores predeterminados de la tarifa
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
                <td><input type="text" name="Valor_Horas" class="form-control" value="${tarifa.valorHora || 0}"></td>
                <td><input type="text" name="Dias" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Dias" class="form-control" value="${tarifa.valorDia || 0}"></td>
                <td><input type="text" name="Meses" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Meses" class="form-control" value="${tarifa.valorMes || 0}"></td>
                <td><input type="text" name="Bolsa" class="form-control" value="${tarifa.bolsaMes || 0}"></td>
                <td><input type="text" name="Valor_Bolsa" class="form-control" value="${tarifa.valorBolsa || 0}"></td>
                <td><input type="text" name="Valor" class="form-control" value=""disabled></td>
                <td><input type="text" name="Descripcion" class="form-control" value=""></td>
                <td><input type="text" name="Numero_Factura" class="form-control" value=""></td>
                <td><input type="text" name="IVA" class="form-control" value="${tarifa.iva || 0}"></td>
                <td><input type="text" name="Referencia" class="form-control" value="${tarifa.referenciaId?.codigoReferencia || ''}"></td>
                <td><input type="text" name="Ceco" class="form-control" value="${tarifa.centrocostosId?.codigoCeCo || ''}"></td>
                <td><input type="text" name="Sitio_Serv" class="form-control" value="${tarifa.sitioTrabajo || ''}"></td>
            `;
            tbody.appendChild(newRow);
    
            // Ocultar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addLineModal'));
            modal.hide();

            // Ocultar el mensaje de "Agregando..."
            addingMessage.style.display = 'none';

            // Procesar la tarifa
            console.log('Tarifa:', tarifa);
        })
        .catch(error => {
            console.error('Error al obtener la tarifa:', error);
            showMessage('Error al obtener la tarifa asociada.', 'danger');
            // Ocultar el mensaje de "Agregando..." en caso de error
            addingMessage.style.display = 'none';
        });
    }

    // Función para generar la plantilla en formato Excel o JPG
    function generateTemplate(format) {
        const rows = document.querySelectorAll('tbody tr'); // Selecciona todas las filas
        const data = [];

        let subtotal = 0;
        let ivaTotal = 0;

        // Recopilar los datos de la tabla
        rows.forEach(row => {
            try {
                // Verificar si la fila tiene los campos necesarios
                const referencia = row.querySelector('input[name="Referencia"]')?.value || '';
                const descripcion = row.querySelector('input[name="Descripcion"]')?.value || '';
                const horas = parseFloat(row.querySelector('input[name="Horas"]')?.value) || 0;
                const valor_horas = parseFloat(row.querySelector('input[name="Valor_Horas"]')?.value) || 0;
                const dias = parseFloat(row.querySelector('input[name="Dias"]')?.value) || 0;
                const valor_dias = parseFloat(row.querySelector('input[name="Valor_Dias"]')?.value) || 0;
                const meses = parseFloat(row.querySelector('input[name="Meses"]')?.value) || 0;
                const valor_meses = parseFloat(row.querySelector('input[name="Valor_Meses"]')?.value) || 0;
                const ceco = row.querySelector('input[name="Ceco"]')?.value || '';
                const sitio_serv = row.querySelector('input[name="Sitio_Serv"]')?.value || '';
                const iva = parseFloat(row.querySelector('input[name="IVA"]')?.value) || 0; // Obtener IVA de la fila

                // Calcular el valor total de la fila
                const valor_total = (horas * valor_horas) + (dias * valor_dias) + (meses * valor_meses);
                subtotal += valor_total;
                ivaTotal += valor_total * (iva / 100); // Calcular IVA basado en el valor de la fila

                if (horas !== 0 && dias !== 0 && meses !== 0){
                    // Agregar los datos necesarios para la plantilla
                    data.push({
                        Referencia: referencia,
                        Concepto: descripcion,
                        Cantidad: horas || dias || meses, // Cantidad puede ser horas, días o meses
                        Valor_Unitario: valor_horas || valor_dias || valor_meses, // Valor unitario correspondiente
                        Valor_Total: valor_total.toFixed(2),
                        Ceco: ceco,
                        Sitio_Serv: sitio_serv
                    });
                }

            } catch (error) {
                console.error('Error procesando fila:', error);
            }
        });

        // Agregar subtotal, IVA y total
        data.push({
            Referencia: '',
            Concepto: 'Subtotal',
            Cantidad: '',
            Valor_Unitario: '',
            Valor_Total: subtotal.toFixed(2),
            Ceco: '',
            Sitio_Serv: ''
        });

        data.push({
            Referencia: '',
            Concepto: 'IVA',
            Cantidad: '',
            Valor_Unitario: `${((ivaTotal / subtotal) * 100).toFixed(2)}%`, // Mostrar el porcentaje
            Valor_Total: ivaTotal.toFixed(2), // Usar IVA calculado
            Ceco: '',
            Sitio_Serv: ''
        });

        data.push({
            Referencia: '',
            Concepto: 'Total',
            Cantidad: '',
            Valor_Unitario: '',
            Valor_Total: (subtotal + ivaTotal).toFixed(2),
            Ceco: '',
            Sitio_Serv: ''
        });

        // Enviar los datos al servidor para generar el archivo
        fetch('/clientes_factura/generar_plantilla/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ data: data, format: format })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `plantilla.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(`Error al generar la plantilla en ${format.toUpperCase()}.`, 'danger');
        });
    }

    // Función para generar la plantilla en formato Excel
    function generateTemplateExcel() {
        generateTemplate('xlsx');
    }

    // Función para generar la plantilla en formato JPG
    function generateTemplateJpg() {
        generateTemplate('jpg');
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
        const generateTemplateButton = document.getElementById('generate-template');

        if (anio && mes && window.searchPerformed) {
            saveButton.removeAttribute('disabled');
            
        } else {
            saveButton.setAttribute('disabled', 'disabled');
        }

        if (anio && mes && cliente && window.searchPerformed) {
            addLineButton.removeAttribute('disabled');
            generateTemplateButton.removeAttribute('disabled');
        } else {
            addLineButton.setAttribute('disabled', 'disabled');
            generateTemplateButton.setAttribute('disabled', 'disabled');
        }
    }

    // Añadir evento para habilitar o deshabilitar los botones
    document.querySelector('select[name="Anio"]').addEventListener('change', function () {
        window.searchPerformed = false;
        toggleButtons();
    });
    document.querySelector('select[name="Mes"]').addEventListener('change', function () {
        window.searchPerformed = false;
        toggleButtons();
    });
    document.querySelector('select[name="ClienteId"]').addEventListener('change', function () {
        window.searchPerformed = false;
        toggleButtons();
    });    

    // Marcar la búsqueda en el submit y persistirla
    document.querySelector('form').addEventListener('submit', function () {
        window.searchPerformed = true;
        sessionStorage.setItem('searchPerformed', 'true');
        toggleButtons(); // Re-evaluar los botones después de la búsqueda
    });    

    // Hacer las funciones accesibles globalmente
    window.generateTemplateExcel = generateTemplateExcel;
    window.generateTemplateJpg = generateTemplateJpg;

    window.saveAllRows = saveAllRows;
    window.confirmAddLine = confirmAddLine;
    window.removeLine = removeLine;
    recalculateTotals(); // Initial calculation
    toggleButtons();
});