document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Recuperar los valores de año y mes originales desde la URL y almacenarlos en localStorage
    updateAnioMesFromURL();

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Variables para rastrear cambios
    let hasUnsavedChanges = false;
    let originalValues = {};

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
    // Mensajes de alerta seguros: crean el DOM si no existe
    function showMessage(message, type = 'info') {
        let alertBox = document.getElementById('message-box');
        let alertIcon = document.getElementById('alert-icon');
        let alertMessage = document.getElementById('alert-message');

        // Si no existen, los creamos como fallback y los añadimos al body
        if (!alertBox || !alertIcon || !alertMessage) {
            alertBox = document.createElement('div');
            alertBox.id = 'message-box';
            // estilos mínimos para que se muestre sin depender del layout
            alertBox.className = `alert alert-${type} alert-dismissible fade show`;
            alertBox.style.position = 'fixed';
            alertBox.style.top = '20px';
            alertBox.style.right = '20px';
            alertBox.style.zIndex = '2050';
            alertBox.style.display = 'none';

            alertIcon = document.createElement('span');
            alertIcon.id = 'alert-icon';
            alertIcon.className = 'alert-heading me-2';

            alertMessage = document.createElement('span');
            alertMessage.id = 'alert-message';

            alertBox.appendChild(alertIcon);
            alertBox.appendChild(alertMessage);
            document.body.appendChild(alertBox);
        }

        // Rellenar y mostrar
        alertMessage.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        const icons = { success: '✔️', danger: '❌', warning: '⚠️', info: 'ℹ️' };
        alertIcon.textContent = icons[type] || '';
        alertBox.style.display = 'block';

        // Ocultar automáticamente después de 3s (seguro: comprueba existencia)
        setTimeout(() => {
            if (alertBox && alertBox.classList) alertBox.classList.remove('show');
            setTimeout(() => {
                if (alertBox && alertBox.style) alertBox.style.display = 'none';
            }, 300);
        }, 3000);
    }


    // Funciones para manejar selecciones
    function toggleButtons() {
        const selectedIds = getSelectedRows();
        sessionStorage.setItem('selectedRows', JSON.stringify(selectedIds)); // Guardar en sessionStorage
        document.getElementById('delete-button').disabled = selectedIds.length === 0;
        document.getElementById('generate-template').disabled = selectedIds.length === 0;
        
        // Activar el botón de guardar si hay selección
        const anio = document.querySelector('select[name="Anio"]').value;
        const mes = document.querySelector('select[name="Mes"]').value;
        document.getElementById('save-button').disabled = !(anio && mes && selectedIds.length > 0);
    }

    document.querySelectorAll('.row-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const allChecked = document.querySelectorAll('.row-checkbox:checked').length === 
                             document.querySelectorAll('.row-checkbox').length;
            document.getElementById('select-all').checked = allChecked;
            toggleButtons();
        });
    });

    // Modificar el evento del select-all
    document.getElementById('select-all').addEventListener('change', function() {
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        toggleButtons(); // Añadir esta línea para actualizar los botones
    });

    // Función de eliminación 
    window.deleteSelectedRows = function() {
        const selectedIds = getSelectedRows();
        if (selectedIds.length === 0) return;

        // Guardar el elemento con foco actual
        window.preDeleteFocusElement = document.activeElement;

        // Mostrar el modal de confirmación
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
        const confirmDeleteButton = document.getElementById('confirmDelete');

        // Limpiar event listeners previos
        confirmDeleteButton.replaceWith(confirmDeleteButton.cloneNode(true));
        const newConfirmDeleteButton = document.getElementById('confirmDelete');

        // Manejar la confirmación de eliminación
        const handleDelete = () => {
            deleteModal.hide();
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

        // Asignar el evento de confirmación
        newConfirmDeleteButton.addEventListener('click', handleDelete, { once: true });

        // Mostrar el modal
        deleteModal.show();
        
    };

    // Función para mostrar modal de confirmación de plantilla POST-GUARDADO
    window.showPostSaveTemplateModal = function() {
        // Cerrar completamente cualquier modal abierto previamente
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
                // Limpiar completamente el modal
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }
        });
        
        // Limpiar backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        
        // Pequeña pausa para asegurar que los modales anteriores estén cerrados
        setTimeout(() => {
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
        }, 50);
    };

   // Guarda de saveAllRows
   function saveAllRows() {
        const data = prepareSaveData();
        console.log('Datos a enviar:', JSON.stringify(data, null, 2)); // Para depuración
        const hasNewRows = data.some(row => !row.ConsecutivoId);
        const selectedIds = getSelectedRows();

        showSavingOverlay(true);
        disableUI(true);

        fetch('/clientes_factura/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ data: data })
        })
        .then(response => {
            if (!response.ok) {
                // Si la respuesta no es exitosa, lanzar un error con el status
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(result => {
            if (result.status === 'success') {
                // Restablecer el estado de cambios
                hasUnsavedChanges = false;
                toggleButtons();
                
                if (hasNewRows && selectedIds.length > 0) {
                    const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
                    const confirmButton = document.getElementById('confirmGenerate');
                    
                    confirmButton.replaceWith(confirmButton.cloneNode(true));
                    const newConfirmButton = document.getElementById('confirmGenerate');

                    const handleConfirmation = () => {
                        confirmationModal.hide();
                        sessionStorage.setItem('pendingTemplateGeneration', JSON.stringify(selectedIds));
                        showPostSaveTemplateModal();
                    };

                    const handleClose = () => {
                        confirmationModal._element.removeEventListener('hidden.bs.modal', handleClose);
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
    
    if (sessionStorage.getItem('showTemplateModal') === 'true') {
        sessionStorage.removeItem('showTemplateModal');
        showTemplateConfirmationModal();
    }
    

    function prepareSaveData() {
        const selectedIds = getSelectedRows();
        const rows = document.querySelectorAll('tbody tr');
        const data = [];
    
        rows.forEach((row) => {
            const rowId = row.id.replace('row-', '');
            
            // Solo procesar filas seleccionadas
            if (selectedIds.includes(rowId)) {
                const rowData = {};
                const inputs = row.querySelectorAll('input');
                
                // Obtener todos los valores de los inputs
                inputs.forEach(input => {
                    if (input.name && input.type !== 'checkbox') {
                        // Campos que deben convertirse a número
                        const numericFields = ['Horas', 'Dias', 'Meses', 'Bolsa', 'Valor', 'IVA', 'LineaId', 'ModuloId'];
                        if (numericFields.includes(input.name)) {
                            // Convertir vacíos a 0 y manejar valores no numéricos
                            const value = input.value.trim();
                            rowData[input.name] = value === '' ? 0 : parseFloat(value) || 0;
                        } else {
                            // Para otros campos, mantener como string
                            rowData[input.name] = input.value;
                        }
                    }
                });
                
                // Incluir el ID solo para filas existentes
                if (rowId && !rowId.startsWith('new-')) {
                    rowData['ConsecutivoId'] = parseInt(rowId);
                } else {
                    // Para nuevas filas, incluir el flag como string
                    rowData['is_new_line'] = 'true';
                }
                
                // Incluir año y mes originales como números
                rowData['ClienteId'] = parseInt(window.originalCliente);
                rowData['Anio'] = parseInt(window.originalAnio);
                rowData['Mes'] = parseInt(window.originalMes);
        
                data.push(rowData);
            }
        });
    
        return data;
    }

    // Restaurar al cargar
 
    const savedSelection = JSON.parse(sessionStorage.getItem('selectedRows') || '[]');
    savedSelection.forEach(id => {
        const checkbox = document.querySelector(`.row-checkbox[data-id="${id}"]`);
        if (checkbox) checkbox.checked = true;
    });
    sessionStorage.removeItem('selectedRows');
    
    // Guardar valores originales para detectar cambios
    document.querySelectorAll('tbody tr').forEach(row => {
        const rowId = row.id.replace('row-', '');
        originalValues[rowId] = {};
        row.querySelectorAll('input').forEach(input => {
            if (input.name) {
                originalValues[rowId][input.name] = input.value;
            }
        });
    });
        
        // Actualizar botones al cargar
        toggleButtons();
    

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

    // Función para mostrar modal de plantilla - Global
    window.showTemplateConfirmationModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('templateConfirmationModal'));
        modal.show();
    };

    // Función auxiliar para conversión segura de valores
    function safeParseFloat(value) {
        if (value === null || value === undefined || value === '') {
            return 0;
        }
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    }

    // Modificar updateRowTotal para usar la función segura y verificar nulidad
    function updateRowTotal(row) {
        const horasInput = row.querySelector('input[name="Horas"]');
        const valorHorasInput = row.querySelector('input[name="Valor_Horas"]');
        const diasInput = row.querySelector('input[name="Dias"]');
        const valorDiasInput = row.querySelector('input[name="Valor_Dias"]');
        const mesesInput = row.querySelector('input[name="Meses"]');
        const valorMesesInput = row.querySelector('input[name="Valor_Meses"]');
        const bolsaInput = row.querySelector('input[name="Bolsa"]');
        const valorBolsaInput = row.querySelector('input[name="Valor_Bolsa"]');
        
        // Verificar que todos los inputs existan antes de acceder a sus valores
        if (!horasInput || !valorHorasInput || !diasInput || !valorDiasInput || 
            !mesesInput || !valorMesesInput || !bolsaInput || !valorBolsaInput) {
            return;
        }
        
        const horas = safeParseFloat(horasInput.value);
        const valorHoras = safeParseFloat(valorHorasInput.value);
        const dias = safeParseFloat(diasInput.value);
        const valorDias = safeParseFloat(valorDiasInput.value);
        const meses = safeParseFloat(mesesInput.value);
        const valorMeses = safeParseFloat(valorMesesInput.value);
        const bolsa = safeParseFloat(bolsaInput.value);
        const valorBolsa = safeParseFloat(valorBolsaInput.value);
        
        const total = (horas * valorHoras) + 
                    (dias * valorDias) + 
                    (meses * valorMeses) + 
                    (bolsa * valorBolsa);
        
        const valorInput = row.querySelector('input[name="Valor"]');
        if (valorInput) {
            valorInput.value = total.toFixed(2);
        }
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
            // Verificar si la fila tiene los inputs necesarios
            const horasInput = row.querySelector('input[name="Horas"]');
            if (!horasInput) return; // Saltar filas que no son de datos
            
            // Actualizar total de la fila primero
            updateRowTotal(row);
            
            // Sumar a los totales generales usando safeParseFloat
            const horas = safeParseFloat(row.querySelector('input[name="Horas"]').value);
            const dias = safeParseFloat(row.querySelector('input[name="Dias"]').value);
            const meses = safeParseFloat(row.querySelector('input[name="Meses"]').value);
            const bolsa = safeParseFloat(row.querySelector('input[name="Bolsa"]').value);
            const valor = safeParseFloat(row.querySelector('input[name="Valor"]').value);
    
            totals.totalHoras += horas;
            totals.totalDias += dias;
            totals.totalMeses += meses;
            totals.totalBolsa += bolsa;
            totals.totalValor += valor;
        });
    
        // Función auxiliar para actualizar solo si el elemento existe
        const updateIfExists = (selector, value) => {
            const element = document.querySelector(selector);
            if (element) {
                element.textContent = typeof value === 'number' ? value.toFixed(2) : value;
            }
        };
    
        // Actualizar los totales en el pie de página
        updateIfExists('tfoot th[data-total-horas]', totals.totalHoras);
        updateIfExists('tfoot th[data-total-dias]', totals.totalDias);
        updateIfExists('tfoot th[data-total-meses]', totals.totalMeses);
        updateIfExists('tfoot th[data-total-bolsa]', totals.totalBolsa);
        updateIfExists('tfoot th[data-total-valor]', totals.totalValor);
    }

    // Función para verificar cambios en los campos
    function checkForChanges() {
        const selectedIds = getSelectedRows();
        if (selectedIds.length === 0) {
            hasUnsavedChanges = false;
            return;
        }
        
        // Verificar si hay cambios en las filas seleccionadas
        hasUnsavedChanges = false;
        
        selectedIds.forEach(id => {
            const row = document.getElementById(`row-${id}`);
            if (row) {
                row.querySelectorAll('input').forEach(input => {
                    if (input.name && originalValues[id] && originalValues[id][input.name] !== input.value) {
                        hasUnsavedChanges = true;
                    }
                });
            }
        });
        
        toggleButtons();
    }
    // Modificar el evento de input para incluir todos los campos relevantes
    document.addEventListener('input', function(e) {
        const target = e.target;
        const relevantFields = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 
                            'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa', 
                            'Descripcion', 'Numero_Factura', 'IVA', 
                            'Referencia', 'Ceco', 'Sitio_Serv'];
        
        if (relevantFields.includes(target.name)) {
            const row = target.closest('tr');
            if (row) {
                updateRowTotal(row);
                recalculateTotals();
                checkForChanges();
            }
        }
    });

    // Modificar los event listeners para incluir todos los campos relevantes
    document.querySelectorAll('input[name="Horas"], input[name="Valor_Horas"], input[name="Dias"], input[name="Valor_Dias"], input[name="Meses"], input[name="Valor_Meses"], input[name="Bolsa"], input[name="Valor_Bolsa"], input[name="Descripcion"], input[name="Numero_Factura"], input[name="IVA"], input[name="Referencia"], input[name="Ceco"], input[name="Sitio_Serv"]').forEach(input => {
        input.addEventListener('input', () => {
            // Actualizar la fila actual y luego los totales generales
            updateRowTotal(input.closest('tr'));
            recalculateTotals();
            checkForChanges();
        });
    });

    function confirmAddLine() {
        const lineaId = document.getElementById('lineaSelect').value;
        const moduloId = document.getElementById('moduloSelect').value;
        const clienteId = window.originalCliente;
        const anio = window.originalAnio;
        const mes = window.originalMes;
    
        if (!lineaId || !moduloId) {
            showMessage('Seleccione una línea y módulo.', 'warning');
            return;
        }
    
        // Obtener el modal y el mensaje de forma segura
        const modal = document.getElementById('addLineModal');
        const addingMessage = modal ? modal.querySelector('#adding-message') : null;
    
        if (addingMessage) {
            addingMessage.style.display = 'block';
        }
    
        // Deshabilitar botones mientras se procesa
        const buttons = modal.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
        });
    
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
            const newRowId = 'new-' + Date.now(); // ID temporal para la nueva fila
            newRow.setAttribute('id', `row-${newRowId}`);
            newRow.innerHTML = `
                <td>
                    <input type="checkbox" class="row-checkbox" data-id="${newRowId}" checked>
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
                <td><input type="number" name="Horas" class="form-control" value=""></td>
                <td><input type="number" name="Valor_Horas" class="form-control" step="0.01" value="${tarifa.valorHora || 0}"></td>
                <td><input type="number" name="Dias" class="form-control" value=""></td>
                <td><input type="number" name="Valor_Dias" class="form-control" step="0.01" value="${tarifa.valorDia || 0}"></td>
                <td><input type="number" name="Meses" class="form-control" value=""></td>
                <td><input type="number" name="Valor_Meses" class="form-control" step="0.01" value="${tarifa.valorMes || 0}"></td>
                <td><input type="number" name="Bolsa" class="form-control" value=""></td>
                <td><input type="number" name="Valor_Bolsa" class="form-control" step="0.01" value="${tarifa.valorBolsa || 0}"></td>
                <td><input type="number" name="Valor" class="form-control" value="" disabled></td>
                <td><input type="text" name="Descripcion" class="form-control" value=""></td>
                <td><input type="text" name="Numero_Factura" class="form-control" value=""></td>
                <td><input type="number" name="IVA" class="form-control" step="0.01" value="${tarifa.iva || 0}"></td>
                <td><input type="text" name="Referencia" class="form-control" value="${tarifa.referenciaId?.codigoReferencia || ''}"></td>
                <td><input type="text" name="Ceco" class="form-control" value="${tarifa.centrocostosId?.codigoCeCo || ''}"></td>
                <td><input type="text" name="Sitio_Serv" class="form-control" value="${tarifa.sitioTrabajo || ''}"></td>
            `;
            tbody.appendChild(newRow);
    
            // Guardar valores originales
            originalValues[newRowId] = {};
            newRow.querySelectorAll('input').forEach(input => {
                if (input.name) {
                    originalValues[newRowId][input.name] = input.value;
                }
            });
            
            // Agregar event listeners a la nueva fila
            addEventListenersToRow(newRow);
    
            // Ocultar el modal
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
    
            // Recalcular totales
            recalculateTotals();
            
            // Marcar que hay cambios sin guardar
            hasUnsavedChanges = true;
            toggleButtons();
        })
        .catch(error => {
            console.error('Error al obtener la tarifa:', error);
            showMessage('Error al obtener la tarifa asociada.', 'danger');
        })
        .finally(() => {
            // Ocultar el mensaje y habilitar botones
            if (addingMessage) {
                addingMessage.style.display = 'none';
            }
            buttons.forEach(button => {
                button.disabled = false;
            });
        });
    }

    // Función para agregar event listeners a los campos de una fila
    function addEventListenersToRow(row) {
        const relevantFields = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 
                              'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa', 
                              'Descripcion', 'Numero_Factura', 'IVA', 
                              'Referencia', 'Ceco', 'Sitio_Serv'];
        
        relevantFields.forEach(fieldName => {
            const input = row.querySelector(`input[name="${fieldName}"]`);
            if (input) {
                input.addEventListener('input', () => {
                    updateRowTotal(row);
                    recalculateTotals();
                    checkForChanges();
                });
            }
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
        const rowId = row.id.replace('row-', '');
        
        // Eliminar de los valores originales
        if (originalValues[rowId]) {
            delete originalValues[rowId];
        }
        
        row.remove();
        recalculateTotals();
        checkForChanges();
    }

    // Habilitar o deshabilitar los botones según los filtros aplicados
    function toggleButtons() {
        const anio = document.querySelector('select[name="Anio"]').value;
        const mes = document.querySelector('select[name="Mes"]').value;
        const cliente = document.querySelector('select[name="ClienteId"]').value;
        const selectedIds = getSelectedRows();
        
        // Habilitar guardar si hay año, mes y selección
        document.getElementById('save-button').disabled = !(anio && mes && selectedIds.length > 0);
        
        // Habilitar agregar línea si hay año, mes y cliente
        document.getElementById('add-line').disabled = !(anio && mes && cliente);
        
        // Habilitar eliminar y generar plantilla si hay selección
        document.getElementById('delete-button').disabled = selectedIds.length === 0;
        document.getElementById('generate-template').disabled = selectedIds.length === 0;
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

    // Función para manejar correctamente el cierre de modales
    
    // Manejo avanzado de accesibilidad para modales
    function setupAdvancedModalAccessibility() {
        let lastFocusedElement = null;
        
        // Guardar el elemento que tenía el foco antes de abrir cualquier modal
        document.addEventListener('click', function(e) {
            if (e.target.matches('[data-bs-toggle="modal"], [data-bs-target]') || 
                e.target.closest('[data-bs-toggle="modal"], [data-bs-target]')) {
                lastFocusedElement = document.activeElement;
            }
        });

        // Configurar eventos para todos los modales
        document.querySelectorAll('.modal').forEach(modal => {
            // Al mostrar un modal
            modal.addEventListener('shown.bs.modal', function() {
                // Enfocar el primer elemento interactivo del modal
                const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (focusableElements.length > 0) {
                    focusableElements[0].focus();
                }
            });

            // Al ocultar un modal - manejo mejorado
            modal.addEventListener('hidden.bs.modal', function() {
                // Limpiar completamente el backdrop de Bootstrap
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => backdrop.remove());
                document.body.classList.remove('modal-open');
                
                // Forzar el cierre completo del modal
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                
                // Restaurar el foco al elemento que abrió el modal o a un elemento seguro
                setTimeout(() => {
                    if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
                        lastFocusedElement.focus();
                    } else {
                        // Fallback: enfocar un elemento seguro
                        const safeElements = document.querySelectorAll('#save-button, #generate-template, #add-line, #delete-button');
                        if (safeElements.length > 0) {
                            safeElements[0].focus();
                        }
                    }
                }, 100);
            });
        });

        // Sobrescribir funciones de cierre de modales
        const originalGenerateTemplateExcel = window.generateTemplateExcel;
        window.generateTemplateExcel = function() {
            if (originalGenerateTemplateExcel) {
                originalGenerateTemplateExcel();
            }
            forceCloseModal('#generateTemplateModal');
        };

        const originalGenerateTemplateJpg = window.generateTemplateJpg;
        window.generateTemplateJpg = function() {
            if (originalGenerateTemplateJpg) {
                originalGenerateTemplateJpg();
            }
            forceCloseModal('#generateTemplateModal');
        };

        // Mejorar la función de eliminación para manejar correctamente el cierre
        const originalDeleteSelectedRows = window.deleteSelectedRows;
        window.deleteSelectedRows = function() {
            // Guardar el foco actual antes de abrir el modal de confirmación
            window.preDeleteFocusElement = document.activeElement;
            
            if (originalDeleteSelectedRows) {
                originalDeleteSelectedRows();
            }
        };

        // Interceptar la confirmación de eliminación
        document.addEventListener('click', function(e) {
            if (e.target.id === 'confirmDelete' || e.target.closest('#confirmDelete')) {
                // Cerrar el modal de confirmación de manera segura
                setTimeout(() => {
                    forceCloseModal('#deleteConfirmationModal');
                    
                    // Restaurar el foco al elemento que estaba antes de la eliminación
                    if (window.preDeleteFocusElement) {
                        window.preDeleteFocusElement.focus();
                        delete window.preDeleteFocusElement;
                    }
                }, 100);
            }
        });
    }

    // Función para forzar el cierre completo de un modal
    function forceCloseModal(modalSelector) {
        const modal = document.querySelector(modalSelector);
        if (!modal) return;
        
        // Obtener la instancia de Bootstrap del modal
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
        
        // Limpieza adicional para asegurar el cierre completo
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        
        // Remover backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remover clase modal-open del body
        document.body.classList.remove('modal-open');
        
        // Mover el foco a un elemento seguro
        setTimeout(() => {
            const safeElements = document.querySelectorAll('#save-button, #generate-template, #add-line, #delete-button');
            if (safeElements.length > 0) {
                safeElements[0].focus();
            }
        }, 150);
    }

    // Inicializar cuando el documento esté listo
    setupAdvancedModalAccessibility();
    

    // Sobrescribir la función showPostSaveTemplateModal para manejar mejor el foco
    if (window.showPostSaveTemplateModal) {
        const originalShowPostSaveTemplateModal = window.showPostSaveTemplateModal;
        window.showPostSaveTemplateModal = function() {
            // Guardar el elemento actual con foco
            window.lastFocusedBeforeModal = document.activeElement;
            
            // Llamar a la función original
            originalShowPostSaveTemplateModal();
            
            // Configurar el manejo del cierre para este modal específico
            const modal = document.getElementById('generateTemplateModal');
            if (modal) {
                const handleHide = function() {
                    // Restaurar el foco al elemento anterior
                    if (window.lastFocusedBeforeModal) {
                        window.lastFocusedBeforeModal.focus();
                    }
                    modal.removeEventListener('hidden.bs.modal', handleHide);
                };
                
                modal.addEventListener('hidden.bs.modal', handleHide);
            }
        };
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
    
    // Inicializar
    recalculateTotals(); // Initial calculation
    toggleButtons(); // Inicializar estado de botones
});