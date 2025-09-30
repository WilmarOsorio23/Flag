document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Variable para controlar el estado de inicialización
    window.isInitializing = true;

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

    function setupCheckboxListeners() {
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const allChecked = document.querySelectorAll('.row-checkbox:checked').length === 
                                 document.querySelectorAll('.row-checkbox').length;
                document.getElementById('select-all').checked = allChecked;
                toggleButtons();
            });
        });
    
        document.getElementById('select-all').addEventListener('change', function() {
            document.querySelectorAll('.row-checkbox').forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            toggleButtons();
        });
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
        if (selectedIds.length === 0) {
            window.showError('No hay filas seleccionadas para eliminar.');
            return;
        }

        window.preDeleteFocusElement = document.activeElement;

        const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
        const confirmDeleteButton = document.getElementById('confirmDelete');

        confirmDeleteButton.replaceWith(confirmDeleteButton.cloneNode(true));
        const newConfirmDeleteButton = document.getElementById('confirmDelete');

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
                    window.showSuccess('Filas eliminadas correctamente.');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    throw new Error('Error en la respuesta del servidor');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.showError('Error al eliminar las filas.');
            })
            .finally(() => showSavingOverlay(false));
            showMessage('Eliminado Exitosamente.','success')
        };

        newConfirmDeleteButton.addEventListener('click', handleDelete, { once: true });
        deleteModal.show();
    };

    // Función para mostrar modal de confirmación de plantilla POST-GUARDADO
    window.showPostSaveTemplateModal = function() {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }
        });
        
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        
        setTimeout(() => {
            const modal = new bootstrap.Modal(document.getElementById('generateTemplateModal'));
            
            const handleClose = () => {
                modal._element.removeEventListener('hidden.bs.modal', handleClose);
                if (sessionStorage.getItem('templateGenerated') === 'true') {
                    sessionStorage.removeItem('templateGenerated');
                    window.location.reload();
                }
            };
            
            modal._element.addEventListener('hidden.bs.modal', handleClose);
            modal.show();
        }, 50);
    };

    // Guarda de saveAllRows
    window.saveAllRows = function() {
        const data = prepareSaveData();
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
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                window.showSuccess('Cambios guardados correctamente.');
                
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
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            window.showError('Error al guardar los cambios: ' + error.message);
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
            if (!rowId) return;
    
            // Incluir si está seleccionada O si tiene cambios respecto a originalValues 
            const lineaInput = row.querySelector('input[name="LineaId"]');
            if (selectedLinea && lineaInput && parseInt(lineaInput.value, 10) !== parseInt(selectedLinea, 10)) {
                return;
            }
            
            const include = selectedIds.includes(rowId) || hasRowChanges(row, rowId);
            if (!include) return;
    
            const rowData = {};
            const inputs = row.querySelectorAll('input');
    
            inputs.forEach(input => {
                if (input.name && input.type !== 'checkbox') {
                    const numericFields = ['Horas', 'Dias', 'Meses', 'Bolsa', 'Valor', 'IVA'];
                    if (numericFields.includes(input.name)) {
                        const value = input.value.trim();
                        rowData[input.name] = value === '' ? 0 : parseFloat(value) || 0;
                    } else {
                        rowData[input.name] = input.value;
                    }
                }
            });
    
            if (rowId && !rowId.startsWith('new-')) {
                rowData['ConsecutivoId'] = parseInt(rowId, 10);
            } else {
                rowData['is_new_line'] = 'true';
            }
    
            rowData['ClienteId'] = parseInt(window.originalCliente, 10);
            rowData['Anio'] = parseInt(window.originalAnio, 10);
            rowData['Mes'] = parseInt(window.originalMes, 10);
    
            const lineaRaw = row.querySelector('input[name="LineaId"]')?.value ?? '';
            const moduloRaw = row.querySelector('input[name="ModuloId"]')?.value ?? '';
            rowData['LineaId'] = parseInt(lineaRaw || '0', 10);
            rowData['ModuloId'] = parseInt(moduloRaw || '0', 10);
    
            if (!rowData['LineaId'] || !rowData['ModuloId']) {
                console.warn('Fila omitida por falta de LineaId/ModuloId', rowId, rowData);
                return; // no la envíes si faltan IDs
            }
    
            data.push(rowData);
        });
    
        console.log(data);
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
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
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

    // FUNCIÓN MEJORADA: Limpiar formato de moneda para convertir a número
    function cleanCurrencyValue(value) {
        if (value === null || value === undefined || value === '') {
            return '0';
        }
        
        const strValue = String(value).trim();
        
        // Si el valor ya es un número sin caracteres especiales, retornarlo tal cual
        if (/^-?\d*\.?\d+$/.test(strValue)) {
            return strValue;
        }
        
        // Remover símbolos de moneda pero preservar puntos decimales
        // Estrategia: preservar solo números, puntos decimales y signo negativo
        let cleaned = strValue.replace(/[$,]/g, ''); // Eliminar $ y comas
        
        // Verificar si hay un punto decimal válido (solo uno y seguido de dígitos)
        const decimalParts = cleaned.split('.');
        
        if (decimalParts.length > 2) {
            // Si hay múltiples puntos, probablemente son separadores de miles
            // Unir todas las partes excepto la última (que sería decimal)
            cleaned = decimalParts.slice(0, -1).join('') + '.' + decimalParts[decimalParts.length - 1];
        }
        
        // Asegurar que solo haya dígitos y un punto decimal opcional
        cleaned = cleaned.replace(/[^\d.-]/g, '');
        
        // Si después de limpiar está vacío, retornar '0'
        if (cleaned === '' || cleaned === '-') {
            return '0';
        }
        
        return cleaned;
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    

    // Función para mostrar modal de plantilla - Global
    window.showTemplateConfirmationModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('templateConfirmationModal'));
        modal.show();
    };

    // Función auxiliar para conversión segura de valores
    // FUNCIÓN MEJORADA: Conversión segura de valores
    function safeParseFloat(value) {
        const cleanedValue = cleanCurrencyValue(value);
        
        // Casos especiales
        if (cleanedValue === '') return 0;
        if (cleanedValue === '.') return 0;
        
        // Para valores como "53.0", parseFloat los maneja correctamente como 53.0
        const parsed = parseFloat(cleanedValue);
        return isNaN(parsed) ? 0 : parsed;
    }

    // NUEVA FUNCIÓN: Formatear valor preservando los decimales originales
    function preserveOriginalFormat(value) {
        if (value === null || value === undefined || value === '') {
            return '';
        }
        
        // Si ya es un número, convertirlo a string sin forzar decimales
        if (typeof value === 'number') {
            // Preservar los decimales originales
            return value.toString();
        }
        
        // Si es string, mantenerlo tal cual
        return String(value);
    }

    // NUEVA FUNCIÓN: Aplicar formato suave que preserve los valores originales
    function applySoftFormatting() {
        
        document.querySelectorAll('input[name="Valor_Horas"], input[name="Valor_Dias"], input[name="Valor_Meses"], input[name="Valor_Bolsa"]').forEach(input => {
            // Solo preservar el formato original, no forzar cambios
            if (input.value && input !== document.activeElement) {
                // Mantener el valor original sin modificaciones
                const currentValue = input.value;
                // Solo limpiar si tiene caracteres no numéricos problemáticos
                if (/[^0-9.,]/.test(currentValue)) {
                    input.value = currentValue.replace(/[^0-9.,]/g, '');
                }
            }
        });
    }

    function getNumericValueFromCell(row, fieldName) {
        // Primero intentar con input
        let input = row.querySelector(`input[name="${fieldName}"]`);
        if (input) {
            return safeParseFloat(input.value);
        }
        
        // Si no hay input, buscar en el contenido de texto de la celda
        const cells = row.querySelectorAll('td');
        let headerIndex = -1;
        
        // Encontrar el índice de la columna basado en los headers
        const headers = document.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            if (header.textContent.trim().includes(fieldName.replace('_', ' '))) {
                headerIndex = index;
            }
        });
        
        if (headerIndex !== -1 && cells[headerIndex]) {
            const cellValue = cells[headerIndex].textContent || cells[headerIndex].innerText;
            return safeParseFloat(cellValue);
        }
        
        return 0;
    }

    // Modificar updateRowTotal para preservar formatos originales
    function updateRowTotal(row) {
        
        // Obtener valores usando la función mejorada
        const horas = getNumericValueFromCell(row, 'Horas');
        const valorHoras = getNumericValueFromCell(row, 'Valor_Horas');
        const dias = getNumericValueFromCell(row, 'Dias');
        const valorDias = getNumericValueFromCell(row, 'Valor_Dias');
        const meses = getNumericValueFromCell(row, 'Meses');
        const valorMeses = getNumericValueFromCell(row, 'Valor_Meses');
        const bolsa = getNumericValueFromCell(row, 'Bolsa');
        const valorBolsa = getNumericValueFromCell(row, 'Valor_Bolsa');
                
        const total = (horas * valorHoras) + 
                    (dias * valorDias) + 
                    (meses * valorMeses) + 
                    (bolsa * valorBolsa);
                
        // Actualizar el input hidden de Valor
        const valorInput = row.querySelector('input[name="Valor"]');
        if (valorInput) {
            valorInput.value = total;
        }
        
        // Actualizar el span visible que muestra el valor
        let valorSpan = row.querySelector('span.form-control-plaintext');
        if (!valorSpan) {
            // Buscar en la celda de Total
            const cells = row.querySelectorAll('td');
            const headers = document.querySelectorAll('thead th');
            let totalIndex = -1;
            
            headers.forEach((header, index) => {
                if (header.textContent.trim().includes('Total')) {
                    totalIndex = index;
                }
            });
            
            if (totalIndex !== -1 && cells[totalIndex]) {
                valorSpan = cells[totalIndex].querySelector('span');
                if (!valorSpan) {
                    // Si no hay span, crear uno
                    valorSpan = document.createElement('span');
                    valorSpan.className = 'form-control-plaintext';
                    cells[totalIndex].innerHTML = '';
                    cells[totalIndex].appendChild(valorSpan);
                }
            }
        }
        
        if (valorSpan) {
            // Aplicar formato de moneda al total de la fila individual
            valorSpan.textContent = formatCurrency(total);
        }
        
        // También buscar por name="valorspan" por si acaso
        const valorSpanByName = row.querySelector('span[name="valorspan"]');
        if (valorSpanByName) {
            valorSpanByName.textContent = formatCurrency(total);
        }
        
        return total;
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
    
        rows.forEach((row, index) => {
            // Verificar si es una fila de datos (tiene inputs)
            const hasInputs = row.querySelector('input[name="Horas"]') !== null;
            if (!hasInputs) {
                return;
            }
            
            
            // Actualizar total de la fila
            const rowTotal = updateRowTotal(row);
            
            // Sumar a los totales generales usando la función mejorada
            const horas = getNumericValueFromCell(row, 'Horas');
            const dias = getNumericValueFromCell(row, 'Dias');
            const meses = getNumericValueFromCell(row, 'Meses');
            const bolsa = getNumericValueFromCell(row, 'Bolsa');
            const valor = rowTotal;
    
            totals.totalHoras += horas;
            totals.totalDias += dias;
            totals.totalMeses += meses;
            totals.totalBolsa += bolsa;
            totals.totalValor += valor;
            
        });
    
        
        // Función auxiliar para actualizar elementos en el footer
        const updateIfExists = (selector, value, isCurrency = false) => {
            const element = document.querySelector(selector);
            if (element) {
                // Aplicar formato de moneda si corresponde
                if (isCurrency) {
                    element.textContent = formatCurrency(value);
                } else {
                    element.textContent = value;
                }
            } else {
                console.log(`❌ Elemento no encontrado: ${selector}`);
            }
        };
    
        // Actualizar los totales en el pie de página
        updateIfExists('tfoot th[data-total-horas]', totals.totalHoras);
        updateIfExists('tfoot th[data-total-dias]', totals.totalDias);
        updateIfExists('tfoot th[data-total-meses]', totals.totalMeses);
        updateIfExists('tfoot th[data-total-bolsa]', totals.totalBolsa);
        updateIfExists('tfoot th[data-total-valor]', totals.totalValor, true); // Este es el único que lleva formato de moneda
        
    }

    // Función para verificar cambios en los campos
    function checkForChanges() {
        hasUnsavedChanges = false;
    
        document.querySelectorAll('tbody tr').forEach(row => {
            const rowId = row.id.replace('row-', '');
            if (rowId && hasRowChanges(row, rowId)) {
                hasUnsavedChanges = true;
            }
        });
    
        toggleButtons();
    }     

    function setupRealTimeCalculations() {
        
        // Event listener general para todos los inputs relevantes
        document.addEventListener('input', function(e) {
            // No procesar eventos durante la inicialización
            if (window.isInitializing) return;
            
            const target = e.target;
            const relevantFields = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 
                                'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa'];
            
            if (relevantFields.includes(target.name)) {
                const row = target.closest('tr');
                if (row) {
                    updateRowTotal(row);
                    recalculateTotals();
                    checkForChanges();
                    toggleButtons();
                }
            }
        });

        // Event listeners específicos para cada campo
        const relevantFields = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 
                              'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa'];
        
        relevantFields.forEach(fieldName => {
            document.querySelectorAll(`input[name="${fieldName}"]`).forEach(input => {
                // Función separada para manejar cambios de input
                const handleInputChange = function() {
                    if (window.isInitializing) return;
                    
                    const row = this.closest('tr');
                    if (row) {
                        updateRowTotal(row);
                        recalculateTotals();
                        checkForChanges();
                    }
                };
                
                // Remover event listeners existentes para evitar duplicados
                input.removeEventListener('input', handleInputChange);
                input.addEventListener('input', handleInputChange);
            });
        });
        
    }

    // Modificar el evento de input para incluir todos los campos relevantes
    document.addEventListener('input', function(e) {
        // No procesar eventos durante la inicialización
        if (window.isInitializing) return;
        
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

    // Modificar los event listeners para preservar formatos originales
    document.querySelectorAll('input[name="Horas"], input[name="Valor_Horas"], input[name="Dias"], input[name="Valor_Dias"], input[name="Meses"], input[name="Valor_Meses"], input[name="Bolsa"], input[name="Valor_Bolsa"], input[name="Descripcion"], input[name="Numero_Factura"], input[name="IVA"], input[name="Referencia"], input[name="Ceco"], input[name="Sitio_Serv"]').forEach(input => {
        const handleInputChange = function() {
            if (window.isInitializing) return;
            
            // Actualizar la fila actual y luego los totales generales
            updateRowTotal(input.closest('tr'));
            recalculateTotals();
            checkForChanges();
        };
        
        input.removeEventListener('input', handleInputChange);
        input.addEventListener('input', handleInputChange);
    });

    window.confirmAddLine = function() {
        const lineaId = document.getElementById('lineaSelect').value;
        const moduloId = document.getElementById('moduloSelect').value;
        const clienteId = window.originalCliente;
        const anio = window.originalAnio;
        const mes = window.originalMes;
    
        if (!lineaId || !moduloId) {
            window.showWarning('Seleccione una línea y módulo.');
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
                <td><input type="text" name="Valor_Horas" class="form-control" value="${tarifa.valorHora || 0}"></td>
                <td><input type="number" name="Dias" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Dias" class="form-control" value="${tarifa.valorDia || 0}"></td>
                <td><input type="number" name="Meses" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Meses" class="form-control" value="${tarifa.valorMes || 0}"></td>
                <td><input type="number" name="Bolsa" class="form-control" value=""></td>
                <td><input type="text" name="Valor_Bolsa" class="form-control" value="${tarifa.valorBolsa || 0}"></td>
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
            window.showError('Error al obtener la tarifa asociada.');
            // Ocultar el mensaje de "Agregando..." en caso de error
            addingMessage.style.display = 'none';
        });
    }

    // Función para agregar event listeners a los campos de una fila
    function addEventListenersToRow(row) {
        
        const relevantFields = ['Horas', 'Valor_Horas', 'Dias', 'Valor_Dias', 
                              'Meses', 'Valor_Meses', 'Bolsa', 'Valor_Bolsa'];
        
        relevantFields.forEach(fieldName => {
            const input = row.querySelector(`input[name="${fieldName}"]`);
            if (input) {
                const handleInputChange = function() {
                    if (window.isInitializing) return;
                    
                    updateRowTotal(row);
                    recalculateTotals();
                    checkForChanges();
                };
                
                input.addEventListener('input', handleInputChange);
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
                        Valor_Unitario: Valor_Unitario,
                        Valor_Total: valor_total,
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
            Valor_Total: subtotal,
            Ceco: '',
            Sitio_Serv: ''
        });

        data.push({
            Referencia: '',
            Concepto: 'IVA',
            Cantidad: '',
            Valor_Unitario: `${((ivaTotal / subtotal) * 100)}%`,
            Valor_Total: ivaTotal,
            Ceco: '',
            Sitio_Serv: ''
        });

        data.push({
            Referencia: '',
            Concepto: 'Total',
            Cantidad: '',
            Valor_Unitario: '',
            Valor_Total: (subtotal + ivaTotal),
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
            window.showError(`Error al generar la plantilla en ${format.toUpperCase()}.`);
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
    window.removeLine = function(button) {
        const row = button.closest('tr');
        const rowId = row.id.replace('row-', '');
        
        // Eliminar de los valores originales
        if (originalValues[rowId]) {
            delete originalValues[rowId];
        }
        
        row.remove();
        recalculateTotals();
        checkForChanges();
        toggleButtons();
    }

    function checkChangesInSelectedRows(selectedIds) {
        if (selectedIds.length === 0) return false;
        
        for (const id of selectedIds) {
            const row = document.getElementById(`row-${id}`);
            if (row && hasRowChanges(row, id)) {
                return true;
            }
        }
        return false;
    }
    
    function hasRowChanges(row, rowId) {
        if (!originalValues[rowId]) {
            return true;
        }
        
        const inputs = row.querySelectorAll('input[name]:not([type="checkbox"]):not([type="hidden"])');
        for (const input of inputs) {
            const originalValue = originalValues[rowId][input.name];
            const currentValue = input.value;
            
            if (originalValue !== currentValue) {
                return true;
            }
        }
        return false;
    }

    // Habilitar o deshabilitar los botones según los filtros aplicados
    function toggleButtons() {
        const anio = document.querySelector('select[name="Anio"]')?.value;
        const mes = document.querySelector('select[name="Mes"]')?.value;
        const cliente = document.querySelector('select[name="ClienteId"]')?.value;
        const selectedIds = getSelectedRows();
      
        // Regla solicitada: habilitar Guardar cuando hay Año y Mes
        // ...y también cuando hay selección o cambios detectados
        const canSave = !!(anio && mes && (window.searchPerformed || selectedIds.length > 0 || hasUnsavedChanges));
      
        document.getElementById('save-button').disabled = !canSave;
        document.getElementById('add-line').disabled = !(anio && mes && cliente);
        document.getElementById('delete-button').disabled = selectedIds.length === 0;
        document.getElementById('generate-template').disabled = selectedIds.length === 0;
    }

    document.getElementById('addLineModal').addEventListener('show.bs.modal', function (event) {
        const clienteId = window.originalCliente;
        const anio = window.originalAnio;
        const mes = window.originalMes;
    
        if (!clienteId || !anio || !mes) {
            window.showWarning('Primero seleccione un cliente, año y mes.');
            event.preventDefault(); // Importante agregar esto
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
                window.showError('Error al cargar las opciones.');
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

    // NUEVA FUNCIÓN: Preservar los valores originales sin formato adicional
    function preserveOriginalValues() {
        
        // No aplicar ningún formato adicional, mantener los valores tal cual vienen de la base de datos
        document.querySelectorAll('input[name="Valor_Horas"], input[name="Valor_Dias"], input[name="Valor_Meses"], input[name="Valor_Bolsa"]').forEach(input => {
            // Mantener el valor exacto sin modificaciones
        });
        
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

    function initialize() {
        // Asegurar que el overlay esté oculto al iniciar
        showSavingOverlay(false);
        
        // Ocultar cualquier mensaje de alerta al iniciar
        const messageBox = document.getElementById('message-box');
        if (messageBox) {
            messageBox.style.display = 'none';
            messageBox.classList.remove('show');
        }
        
        // Restaurar selección guardada
        const savedSelection = JSON.parse(sessionStorage.getItem('selectedRows') || '[]');
        savedSelection.forEach(id => {
            const checkbox = document.querySelector(`.row-checkbox[data-id="${id}"]`);
            if (checkbox) checkbox.checked = true;
        });
        sessionStorage.removeItem('selectedRows');
        
        // Guardar valores originales
        document.querySelectorAll('tbody tr').forEach(row => {
            const rowId = row.id.replace('row-', '');
            originalValues[rowId] = {};
            row.querySelectorAll('input').forEach(input => {
                if (input.name) {
                    originalValues[rowId][input.name] = input.value;
                }
            });
        });
        
        normalizeRowIds();

        // Configurar event listeners
        setupCheckboxListeners();
        setupRealTimeCalculations();
        
        // Preservar valores originales sin formato adicional
        preserveOriginalValues();
        
        // Calcular totales iniciales
        recalculateTotals();
        toggleButtons();
        
        // Marcar que la inicialización ha terminado
        setTimeout(() => {
            window.isInitializing = false;
        }, 100);
    }

    // Hacer las funciones accesibles globalmente
    window.generateTemplateExcel = generateTemplateExcel;
    window.generateTemplateJpg = generateTemplateJpg;

    window.saveAllRows = saveAllRows;
    window.confirmAddLine = confirmAddLine;
    window.removeLine = removeLine;
    
    // Asegurar que el overlay esté oculto cuando se cierra la página
    window.addEventListener('beforeunload', function() {
        showSavingOverlay(false);
    });

    // También asegurar que esté oculto si hay un error de carga
    window.addEventListener('error', function() {
        showSavingOverlay(false);
    });

    function normalizeRowIds() {
        const rows = document.querySelectorAll('tbody tr');
        let counter = 0;

        rows.forEach((row) => {
            const cb = row.querySelector('.row-checkbox');
            if (!cb) return;
        
            const rawId = (cb.dataset.id || '').trim();
            // si no tiene id, asígnale uno sintético estable
            if (!rawId) {
            const newId = `new-auto-${counter++}`;
            cb.dataset.id = newId;
            row.id = `row-${newId}`;
        
            // añade bandera para que prepareSaveData marque nueva línea
            if (!row.querySelector('input[name="is_new_line"]')) {
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'is_new_line';
                hidden.value = 'true';
                row.appendChild(hidden);
            }
            } else {
            // Asegura que el <tr> tenga id coherente
            if (!row.id || row.id === 'row-') {
                row.id = `row-${rawId}`;
            }
            }
        });
    }
    
    initialize();
});