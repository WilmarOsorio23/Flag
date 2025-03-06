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
     
    // Función para deshabilitar UI
    function disableUI(disable) {
        document.querySelectorAll('input, button, select').forEach(element => {
            if (element.id !== 'saving-overlay') { // Excluir el overlay
                element.disabled = disable;
            }
        });
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

    // Funciones para manejar selecciones
    function toggleDeleteButton() {
        const selectedIds = getSelectedRows();
        sessionStorage.setItem('selectedRows', JSON.stringify(selectedIds)); // Guardar en sessionStorage
        document.getElementById('delete-button').disabled = selectedIds.length === 0;
        document.getElementById('generate-template').disabled = selectedIds.length === 0;
    }

    document.querySelectorAll('.row-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const allChecked = document.querySelectorAll('.row-checkbox:checked').length === 
                             document.querySelectorAll('.row-checkbox').length;
            document.getElementById('select-all').checked = allChecked;
            toggleDeleteButton();
        });
    });

    // Modificar el evento del select-all
    document.getElementById('select-all').addEventListener('change', function() {
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        toggleDeleteButton(); // Añadir esta línea para actualizar los botones
    });

    // Función de eliminación - Modificada para uso global
    window.deleteSelectedRows = function() {
        const selectedIds = getSelectedRows();
        if (selectedIds.length === 0) return;

        if (!confirm('¿Está seguro de eliminar las filas seleccionadas?')) return;

        showSavingOverlay(true);
        
        fetch('/clientes_factura/eliminar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ ids: selectedIds })
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            }
        })
        .finally(() => showSavingOverlay(false));
    };

    // Función para mostrar modal de confirmación de plantilla POST-GUARDADO
    window.showPostSaveTemplateModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('generateTemplateModal'));
        
        const handleClose = () => {
            modal._element.removeEventListener('hidden.bs.modal', handleClose);
            if (sessionStorage.getItem('templateGenerated') === 'true') {
                sessionStorage.removeItem('templateGenerated');
                window.location.reload(); // Forzar recarga solo si se generó plantilla
            }
        };
        
        modal._element.addEventListener('hidden.bs.modal', handleClose);
        modal.show();
    };

   // Guarda de saveAllRows
   function saveAllRows() {
        const selectedIds = getSelectedRows();
        showSavingOverlay(true);
        disableUI(true);

        fetch('/clientes_factura/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ data: prepareSaveData() })
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                if (selectedIds.length > 0) {
                    const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
                    const confirmButton = document.getElementById('confirmGenerate');
                    
                    // Limpiar event listeners previos
                    confirmButton.replaceWith(confirmButton.cloneNode(true));
                    const newConfirmButton = document.getElementById('confirmGenerate');

                    const handleConfirmation = () => {
                        confirmationModal.hide();
                        sessionStorage.setItem('pendingTemplateGeneration', JSON.stringify(selectedIds));
                        showPostSaveTemplateModal();
                    };

                    const handleClose = () => {
                        confirmationModal._element.removeEventListener('hidden.bs.modal', handleClose);
                        // Solo recargar si no se confirmó la generación
                        if (!sessionStorage.getItem('pendingTemplateGeneration')) {
                            window.location.reload();
                        }
                    };

                    confirmationModal._element.addEventListener('hidden.bs.modal', handleClose, {once: true});
                    newConfirmButton.addEventListener('click', handleConfirmation, {once: true});
                    
                    confirmationModal.show();
                } else {
                    window.location.reload();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error al guardar los cambios.', 'danger');
        })
        .finally(() => {
            showSavingOverlay(false);
            disableUI(false);
        });
    }

    // Verificar modal al cargar
    document.addEventListener('DOMContentLoaded', function() {
        if (sessionStorage.getItem('showTemplateModal') === 'true') {
            sessionStorage.removeItem('showTemplateModal');
            showTemplateConfirmationModal();
        }
    });

    function prepareSaveData() {
        const rows = document.querySelectorAll('tbody tr');
        const data = [];
    
        rows.forEach((row) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');
            
            inputs.forEach(input => {
                if (input.name) {
                    rowData[input.name] = input.value;
                }
            });
    
            const rowId = row.id.replace('row-', '');
            if (rowId) rowData['ConsecutivoId'] = rowId;
            
            rowData['Anio'] = window.originalAnio;
            rowData['Mes'] = window.originalMes;
    
            data.push(rowData);
        });
    
        return data;
    }

    // Restaurar al cargar
    document.addEventListener('DOMContentLoaded', function() {
        const savedSelection = JSON.parse(sessionStorage.getItem('selectedRows') || '[]');
        savedSelection.forEach(id => {
            const checkbox = document.querySelector(`.row-checkbox[data-id="${id}"]`);
            if (checkbox) checkbox.checked = true;
        });
        sessionStorage.removeItem('selectedRows');
    });

    function showSavingOverlay(show) {
        const overlay = document.getElementById('saving-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    function getSelectedRows() {
        const selectedIds = Array.from(document.querySelectorAll('.row-checkbox:checked'))
            .map(checkbox => {
                const id = checkbox.dataset.id || checkbox.closest('tr').id.replace('row-', '');
                return id;
            })
            .filter(id => id && id !== "undefined");
        return selectedIds;
    }

    // Eliminar filas seleccionadas
    window.deleteSelectedRows = function() {
        const selectedIds = getSelectedRows();
        if (selectedIds.length === 0) return;

        if (!confirm('¿Está seguro de eliminar las filas seleccionadas?')) return;

        showSavingOverlay(true);
        
        fetch('/clientes_factura/eliminar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ ids: selectedIds })
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            }
        })
        .finally(() => showSavingOverlay(false));
    };

    // Función para mostrar modal de plantilla - Global
    window.showTemplateConfirmationModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('templateConfirmationModal'));
        modal.show();
    };

    function updateRowTotal(row) {
        const horas = parseFloat(row.querySelector('input[name="Horas"]').value) || 0;
        const valorHoras = parseFloat(row.querySelector('input[name="Valor_Horas"]').value) || 0;
        const dias = parseFloat(row.querySelector('input[name="Dias"]').value) || 0;
        const valorDias = parseFloat(row.querySelector('input[name="Valor_Dias"]').value) || 0;
        const meses = parseFloat(row.querySelector('input[name="Meses"]').value) || 0;
        const valorMeses = parseFloat(row.querySelector('input[name="Valor_Meses"]').value) || 0;
        const bolsa = parseFloat(row.querySelector('input[name="Bolsa"]').value) || 0;
        const valorBolsa = parseFloat(row.querySelector('input[name="Valor_Bolsa"]').value) || 0;
        
        
        const total = (horas * valorHoras) + (dias * valorDias) + (meses * valorMeses) + (bolsa *  valorBolsa);
        row.querySelector('input[name="Valor"]').value = total.toFixed(2);
    }    

    function recalculateTotals() {
        const rows = document.querySelectorAll('tbody tr');
        const totals = {
            totalHoras: 0,
            totalDias: 0,
            totalMeses: 0,
            totalBolsa: 0,
            totalValor: 0
        };
    
        rows.forEach(row => {
            // Actualizar total de la fila primero
            updateRowTotal(row);
            
            // Sumar a los totales generales
            const horas = parseFloat(row.querySelector('input[name="Horas"]').value) || 0;
            const dias = parseFloat(row.querySelector('input[name="Dias"]').value) || 0;
            const meses = parseFloat(row.querySelector('input[name="Meses"]').value) || 0;
            const bolsa = parseFloat(row.querySelector('input[name="Bolsa"]').value) || 0;
            const valor = parseFloat(row.querySelector('input[name="Valor"]').value) || 0;
    
            totals.totalHoras += horas;
            totals.totalDias += dias;
            totals.totalMeses += meses;
            totals.totalBolsa += bolsa;
            totals.totalValor += valor;
        });
    
        // Actualizar los totales en el pie de página
        document.querySelector('tfoot th[data-total-horas]').textContent = totals.totalHoras.toFixed(0);
        document.querySelector('tfoot th[data-total-dias]').textContent = totals.totalDias.toFixed(0);
        document.querySelector('tfoot th[data-total-meses]').textContent = totals.totalMeses.toFixed(0);
        document.querySelector('tfoot th[data-total-bolsa]').textContent = totals.totalBolsa.toFixed(0);
        document.querySelector('tfoot th[data-total-valor]').textContent = totals.totalValor.toFixed(2);
    }

    // Modificar los event listeners para incluir todos los campos relevantes
    document.querySelectorAll('input[name="Horas"], input[name="Valor_Horas"], input[name="Dias"], input[name="Valor_Dias"], input[name="Meses"], input[name="Valor_Meses"], input[name="Bolsa"], input[name="Valor_Bolsa"]').forEach(input => {
        input.addEventListener('input', () => {
            // Actualizar la fila actual y luego los totales generales
            updateRowTotal(input.closest('tr'));
            recalculateTotals();
        });
    });

    function confirmAddLine() {
        const lineaId = document.getElementById('lineaSelect').value;
        const moduloId = document.getElementById('moduloSelect').value;
        const clienteId = window.originalCliente;
        const anio = window.originalAnio; // Obtener el año del filtro
        const mes = window.originalMes;   // Obtener el mes del filtro
    
        if (!lineaId || !moduloId) {
            showMessage('Seleccione una línea y módulo.', 'warning');
            return;
        }

        // Mostrar el mensaje de "Agregando..."
        const addingMessage = document.getElementById('adding-message');
        addingMessage.style.display = 'block';
    
        // Obtener la tarifa asociada al cliente y la línea
        fetch(`/clientes_factura/obtener_factura/?clienteId=${clienteId}&lineaId=${lineaId}&moduloId=${moduloId}&anio=${anio}&mes=${mes}`, {
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
                </td>
                <td>
                    <input type="text" name="ClienteId" class="form-control" value="${clienteId}" hidden>
                    <input type="hidden" name="is_new_line" value="true">
                </td>
                <td>${document.querySelector('#lineaSelect option:checked').textContent}
                    <input type="text" name="LineaId" class="form-control" value="${lineaId}" hidden>
                </td>
                <td>${document.querySelector('#moduloSelect option:checked').textContent}
                    <input type="text" name="ModuloId" class="form-control" value="${moduloId}" hidden>
                </td>
                <td><input type="text" name="Horas" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Horas" class="form-control" value="${tarifa.valorHora || 0}"></td>
                <td><input type="text" name="Dias" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Dias" class="form-control" value="${tarifa.valorDia || 0}"></td>
                <td><input type="text" name="Meses" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Meses" class="form-control" value="${tarifa.valorMes || 0}"></td>
                <td><input type="text" name="Bolsa" class="form-control" value=""></td>
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

            // Agregar event listeners a los campos de la nueva fila para calcular el valor en tiempo real
            addEventListenersToRow(newRow);

            // Recalcular totales
            recalculateTotals();
        })
        .catch(error => {
            console.error('Error al obtener la tarifa:', error);
            showMessage('Error al obtener la tarifa asociada.', 'danger');
            // Ocultar el mensaje de "Agregando..." en caso de error
            addingMessage.style.display = 'none';
        });
    }

    // Función para agregar event listeners a los campos de una fila
    function addEventListenersToRow(row) {
        const inputs = row.querySelectorAll('input[name="Horas"], input[name="Valor_Horas"], input[name="Dias"], input[name="Valor_Dias"], input[name="Meses"], input[name="Valor_Meses"], input[name="Bolsa"], input[name="Valor_Bolsa"]');

        inputs.forEach(input => {
            input.addEventListener('input', () => {
                // Actualizar el valor total de la fila
                updateRowTotal(row);
                // Recalcular los totales generales
                recalculateTotals();
            });
        });
    }

    // Función para generar la plantilla en formato Excel o JPG
    function generateTemplate(format, selectedIds) {
        const validSelectedIds = selectedIds.filter(id => id && id !== "undefined");

        let rowsToProcess = validSelectedIds.length > 0 
            ? Array.from(document.querySelectorAll('tbody tr')).filter(row => {
                const rowId = row.id.replace('row-', '');
                return validSelectedIds.includes(rowId);
            })
            : [];

        if (rowsToProcess.length === 0) {
            rowsToProcess = Array.from(document.querySelectorAll('tbody tr'));
        }

        const data = [];
        let subtotal = 0;
        let ivaTotal = 0;

        // Recopilar datos solo de las filas seleccionadas
        rowsToProcess.forEach(row => {
            try {
                const referencia = row.querySelector('input[name="Referencia"]')?.value || '';
                const descripcion = row.querySelector('input[name="Descripcion"]')?.value || '';
                const horas = parseFloat(row.querySelector('input[name="Horas"]')?.value) || 0;
                const valor_horas = parseFloat(row.querySelector('input[name="Valor_Horas"]')?.value) || 0;
                const dias = parseFloat(row.querySelector('input[name="Dias"]')?.value) || 0;
                const valor_dias = parseFloat(row.querySelector('input[name="Valor_Dias"]')?.value) || 0;
                const meses = parseFloat(row.querySelector('input[name="Meses"]')?.value) || 0;
                const valor_meses = parseFloat(row.querySelector('input[name="Valor_Meses"]')?.value) || 0;
                const bolsa = parseFloat(row.querySelector('input[name="Bolsa"]')?.value) || 0;
                const valor_bolsa = parseFloat(row.querySelector('input[name="Valor_Bolsa"]')?.value) || 0;
                const ceco = row.querySelector('input[name="Ceco"]')?.value || '';
                const sitio_serv = row.querySelector('input[name="Sitio_Serv"]')?.value || '';
                const iva = parseFloat(row.querySelector('input[name="IVA"]')?.value) || 0;

                const valor_total = (horas * valor_horas) + (dias * valor_dias) + 
                                (meses * valor_meses) + (bolsa * valor_bolsa);
                
                let Valor_Unitario = 0;
                if (horas !== 0) Valor_Unitario = valor_horas;
                else if (dias !== 0) Valor_Unitario = valor_dias;
                else if (meses !== 0) Valor_Unitario = valor_meses;
                else if (bolsa !== 0) Valor_Unitario = valor_bolsa;

                subtotal += valor_total;
                ivaTotal += valor_total * (iva / 100);

                if (horas !== 0 || dias !== 0 || meses !== 0 || bolsa !== 0) {
                    data.push({
                        Referencia: referencia,
                        Concepto: descripcion,
                        Cantidad: horas || dias || meses || bolsa,
                        Valor_Unitario: Valor_Unitario.toFixed(2),
                        Valor_Total: valor_total.toFixed(2),
                        Ceco: ceco,
                        Sitio_Serv: sitio_serv
                    });
                }
            } catch (error) {
                console.error('Error procesando fila:', error);
            }
        });

        // Agregar totales (igual que antes)
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
            Valor_Unitario: `${((ivaTotal / subtotal) * 100).toFixed(2)}%`,
            Valor_Total: ivaTotal.toFixed(2),
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

        return fetch('/clientes_factura/generar_plantilla/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({ 
                data: data, 
                format: format,
                selectedIds: selectedIds,
                timestamp: Date.now() // Parámetro único anti-cache
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Añadir timestamp al nombre del archivo
            const timestamp = new Date().getTime();
            a.download = `plantilla_${format}_${timestamp}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            return true; // Indicar éxito
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(`Error al generar la plantilla en ${format.toUpperCase()}.`, 'danger');
        });
    }

   // Modificar funciones de generación para cerrar el modal
   window.generateTemplateExcel = function() {
        const selectedIds = getSelectedRows();
        const isPostSave = selectedIds.length > 0;

        generateTemplate('xlsx', selectedIds)
        .then(success => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('generateTemplateModal'));
            modal.hide();
            
            if (isPostSave && success) {
                sessionStorage.removeItem('pendingTemplateGeneration');
                window.location.reload(); // Recarga solo post-guardado exitoso
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sessionStorage.removeItem('pendingTemplateGeneration');
        });
    };

    window.generateTemplateJpg = function() {
        const selectedIds = getSelectedRows();
        const isPostSave = selectedIds.length > 0;

        generateTemplate('jpg', selectedIds)
        .then(success => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('generateTemplateModal'));
            modal.hide();
            
            if (isPostSave && success) {
                sessionStorage.removeItem('pendingTemplateGeneration');
                window.location.reload(); // Recarga solo post-guardado exitoso
            }
        })
        .catch(error => {
            console.error('Error:', error);
            sessionStorage.removeItem('pendingTemplateGeneration');
        });
    };

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
        
        // Habilitar guardar si hay año y mes
        document.getElementById('save-button').disabled = !(anio && mes);
        
        // Habilitar agregar línea si hay año, mes y cliente
        document.getElementById('add-line').disabled = !(anio && mes && cliente);
        
        // Habilitar generar plantilla si hay selección
        toggleDeleteButton();
    }

    document.getElementById('addLineModal').addEventListener('show.bs.modal', function (event) {
        const clienteId = window.originalCliente;
        const anio = window.originalAnio;
        const mes = window.originalMes;
    
        if (!clienteId || !anio || !mes) {
            showMessage('Primero seleccione un cliente, año y mes.', 'warning');
            return;
        }
    
        fetch(`/clientes_factura/get_lineas_modulos/?clienteId=${clienteId}&anio=${anio}&mes=${mes}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la solicitud');
                }
                return response.json();
            })
            .then(data => {
                const lineaSelect = document.getElementById('lineaSelect');
                const moduloSelect = document.getElementById('moduloSelect');
    
                // Limpiar y cargar líneas
                lineaSelect.innerHTML = data.lineas.map(linea => 
                    `<option value="${linea.LineaId}">${linea.Linea}</option>`
                ).join('');
    
                // Limpiar y cargar módulos
                moduloSelect.innerHTML = data.modulos.map(modulo => 
                    `<option value="${modulo.ModuloId}">${modulo.Modulo}</option>`
                ).join('');
            })
            .catch(error => {
                console.error('Error al obtener las líneas y módulos:', error);
                showMessage('Error al cargar las opciones.', 'danger');
            });
    });

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