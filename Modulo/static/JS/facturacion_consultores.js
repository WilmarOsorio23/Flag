// Event listeners principales
document.addEventListener('DOMContentLoaded', function() {
    // NO marcar automáticamente las filas con datos como editadas
    // Solo se marcarán como editadas cuando el usuario modifique manualmente un campo

    // Event listeners para campos editables
    document.querySelectorAll('input.form-control:not([readonly])').forEach(input => {
        input.addEventListener('input', () => {
            document.getElementById('save-button').disabled = false;
            // Marcar la fila como editada solo cuando el usuario modifica manualmente
            const row = input.closest('tr');
            if (row) {
                row.dataset.edited = 'true';
            }
        });
    });

    // Actualiza el texto del dropdown al seleccionar/desmarcar opciones
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.nextSibling.textContent.trim());

        if (selectedOptions.length === 0) {
            button.textContent = selectedText;
        } else if (selectedOptions.length === 1) {
            button.textContent = selectedOptions[0];
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`;
        }
    }

    // Meses
    const clienteCheckboxes = document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownMesCobro', clienteCheckboxes)
        )
    );

    // Verificar si hay parámetro de éxito en la URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === '1') {
        mostrarModal();
    }

    // Controla el botón de eliminar según los checkboxes seleccionados
    const checkboxes = document.querySelectorAll('.row-checkbox');
    const btnEliminar = document.getElementById('delete-button');

    function toggleEliminarButton() {
        // Verificar si hay checkboxes seleccionados
        const checkboxesSeleccionados = Array.from(checkboxes).filter(cb => cb.checked);
        
        // Verificar que todos los registros seleccionados sean existentes (no nuevos)
        const todosExistentes = checkboxesSeleccionados.every(cb => {
            const rowId = cb.value;
            return rowId !== 'new' && rowId !== '';
        });
        
        // Solo habilitar el botón si hay registros seleccionados Y todos son existentes
        const algunoSeleccionado = checkboxesSeleccionados.length > 0;
        const puedeEliminar = algunoSeleccionado && todosExistentes;
        
        if (btnEliminar) {
            btnEliminar.disabled = !puedeEliminar;
            
            // Mostrar tooltip o mensaje si se intenta seleccionar registros nuevos
            if (algunoSeleccionado && !todosExistentes) {
                btnEliminar.title = 'No se pueden eliminar registros nuevos. Guárdalos primero.';
            } else {
                btnEliminar.title = '';
            }
        }
    }

    checkboxes.forEach(cb => cb.addEventListener('change', toggleEliminarButton));

    const masterCheckbox = document.getElementById('select-all');
    if (masterCheckbox) {
        masterCheckbox.addEventListener('change', () => {
            const checked = masterCheckbox.checked;
            checkboxes.forEach(cb => cb.checked = checked);
            toggleEliminarButton();
        });
    }

    // Ejecutar una vez al cargar
    toggleEliminarButton();
});

// Función para guardar solo los registros editados
function saveAllRows() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/facturacion_consultores/guardar/';

    // CSRF token
    const csrf = document.querySelector('input[name=csrfmiddlewaretoken]');
    if (csrf) {
        form.appendChild(csrf.cloneNode());
    }

    // Solo recolectar campos de filas que han sido editadas manualmente
    const filasEditadas = document.querySelectorAll('tr[id^="row-"][data-edited="true"]');
    
    console.log('Filas editadas encontradas:', filasEditadas.length);
    
    if (filasEditadas.length === 0) {
        alert('No hay registros editados para guardar.');
        return;
    }

    // Verificar que realmente hay cambios en las filas editadas
    let filasConCambios = 0;
    filasEditadas.forEach(fila => {
        const inputs = fila.querySelectorAll('input.form-control');
        const tieneCambios = Array.from(inputs).some(input => {
            // Para registros nuevos, verificar que al menos un campo editable tenga valor
            const rowId = fila.id.replace('row-', '');
            if (rowId === 'new') {
                return input.value && input.value.trim() !== '';
            }
            // Para registros existentes, verificar que el valor sea diferente del original
            return input.value !== input.defaultValue;
        });
        
        if (tieneCambios) {
            filasConCambios++;
            const rowId = fila.id.replace('row-', '');
            
            // Recolectar todos los campos de la fila editada
            fila.querySelectorAll('input.form-control, input[type=hidden]').forEach(input => {
                const clone = document.createElement('input');
                clone.type = 'hidden';
                clone.name = input.name;
                clone.value = input.value;
                form.appendChild(clone);
            });
        }
    });

    if (filasConCambios === 0) {
        alert('No hay cambios reales para guardar.');
        return;
    }

    console.log('Filas con cambios reales:', filasConCambios);

    // Campos select (Mes, etc.)
    document.querySelectorAll('select').forEach(select => {
        const clone = document.createElement('input');
        clone.type = 'hidden';
        clone.name = select.name;
        clone.value = select.value;
        form.appendChild(clone);
    });

    // Campo oculto adicional para indicar guardado
    const saveFlag = document.createElement('input');
    saveFlag.type = 'hidden';
    saveFlag.name = 'guardar';
    saveFlag.value = '1';
    form.appendChild(saveFlag);

    // Enviar el formulario
    document.body.appendChild(form);
    form.submit();
    
    // Mostrar el modal de confirmación
    mostrarModal('modalConfirmacion');

    // Deshabilitar el botón después de guardar para evitar más clics
    document.getElementById('save-button').disabled = true;
}

// Mostrar mensajes de alerta
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
    }, 1500);
}

// Mostrar modal
function mostrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = "block";
    }
}

// Cerrar modal
function cerrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.style.display = "none";
        const url = new URL(window.location.href);
        url.searchParams.delete('success');
        window.history.replaceState({}, document.title, url.toString());
    }
}

// Función de eliminar registros seleccionados
function eliminarSeleccionados() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    const ids = Array.from(checkboxes).map(cb => cb.value);

    if (ids.length === 0) {
        alert('Selecciona al menos un registro para eliminar.');
        return;
    }

    // Verificar que no se intenten eliminar registros nuevos
    const registrosNuevos = ids.filter(id => id === 'new' || id === '');
    if (registrosNuevos.length > 0) {
        alert('No se pueden eliminar registros nuevos. Guárdalos primero antes de eliminarlos.');
        return;
    }

    if (!confirm('¿Estás seguro de eliminar los registros seleccionados?')) {
        return;
    }

    fetch('/facturacion_consultores/eliminar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage('Registros eliminados correctamente', 'success');
            location.reload(); // Recarga inmediata
        } else {
            showMessage('Error al eliminar: ' + (data.error || 'desconocido'), 'danger');
        }
    })
    .catch(error => {
        showMessage('Error en la petición: ' + error.message, 'danger');
    });
    mostrarModal('modaleliminacion');
}

// Función para actualizar el panel de resumen
document.addEventListener('DOMContentLoaded', function() {
    function actualizarResumen(rowId) {
        const valorFacturaCliente = parseFloat(document.querySelector(`[name="Valor_Factura_Cliente_${rowId}"]`).value) || 0;
        const valorCobro = parseFloat(document.querySelector(`[name="Valor_Cobro_${rowId}"]`).value) || 0;

        // Calcular Diferencia Bruta
        const diferenciaBruta = valorFacturaCliente - valorCobro;
        document.getElementById('diferencia-bruta-actual').textContent = diferenciaBruta.toFixed(2);

        // Calcular % Dif
        const porcentajeDif = (Math.abs(diferenciaBruta) / valorFacturaCliente) * 100;
        document.getElementById('porcentaje-dif-actual').textContent = porcentajeDif.toFixed(2);
    }

    // Escuchar cambios en los campos de cualquier fila
    document.querySelectorAll('[name^="Valor_Factura_Cliente_"], [name^="Valor_Cobro_"]').forEach(input => {
        input.addEventListener('input', function() {
            const rowId = this.name.split('_').pop();
            actualizarResumen(rowId);
        });
    });
});

// Función para actualizar cálculos de diferencia
document.addEventListener('DOMContentLoaded', function () {
    function actualizarCalculo(i) {
        console.log("Actualizando fila:", i);
        const valorCobroInput = document.querySelector(`input[name="Valor_Cobro_${i}"]`);
        const valorFacturaInput = document.querySelector(`input[name="Valor_Factura_Cliente_${i}"]`);
        const porcentajeTd = document.getElementById(`porcentaje-dif-${i}`);
        const diferenciaTd = document.getElementById(`diferencia-bruta-${i}`);

        const hiddenPorcentaje = document.querySelector(`input[name="Porcentaje_Dif_${i}"]`);
        const hiddenDiferencia = document.querySelector(`input[name="Diferencia_Bruta_${i}"]`);

        const valCobro = parseFloat(valorCobroInput?.value) || 0;
        const valFactura = parseFloat(valorFacturaInput?.value);

        // Validar que factura no esté vacía o cero
        if (isNaN(valFactura) || valFactura === 0) {
            if (porcentajeTd?.querySelector('span')) porcentajeTd.querySelector('span').textContent = "0.00";
            if (diferenciaTd?.querySelector('span')) diferenciaTd.querySelector('span').textContent = "0.00";

            if (hiddenPorcentaje) hiddenPorcentaje.value = "0.00";
            if (hiddenDiferencia) hiddenDiferencia.value = "0.00";
            return;
        }

        const diferencia = valFactura - valCobro;
        const porcentaje = Math.abs((diferencia / valFactura) * 100);

        if (porcentajeTd?.querySelector('span')) porcentajeTd.querySelector('span').textContent = porcentaje.toFixed(2);
        if (diferenciaTd?.querySelector('span')) diferenciaTd.querySelector('span').textContent = diferencia.toFixed(2);

        if (hiddenPorcentaje) hiddenPorcentaje.value = porcentaje.toFixed(2);
        if (hiddenDiferencia) hiddenDiferencia.value = diferencia.toFixed(2);
    }

    const filas = document.querySelectorAll('tbody tr[id^="row-"]');
    filas.forEach(fila => {
        const id = fila.id.replace('row-', '');

        const inputCobro = document.querySelector(`input[name="Valor_Cobro_${id}"]`);
        const inputFactura = document.querySelector(`input[name="Valor_Factura_Cliente_${id}"]`);

        [inputCobro, inputFactura].forEach(input => {
            if (input) {
                input.addEventListener('input', () => actualizarCalculo(id));
            }
        });

        actualizarCalculo(id);
    });
});

// Recálculo en línea de campos dependientes
document.addEventListener('DOMContentLoaded', function () {
    function recalcularValores(i) {
        console.log('Ejecutando recalcularValores para fila:', i);
        // Inputs de la fila
        const horasInput = document.querySelector(`input[name="Cantidad_Horas_${i}"]`);
        const valorUnitarioInput = document.querySelector(`input[name="Valor_Unitario_${i}"]`);
        const valorCobroHidden = document.querySelector(`input[name="Valor_Cobro_${i}"]`);
        const valorCobroSpan = document.getElementById(`valor-cobro-span-${i}`);
        const ivaInput = document.getElementById(`iva-input-${i}`);
        const ivaHidden = document.querySelector(`input[name="IVA_${i}"]`);
        const valorNetoHidden = document.querySelector(`input[name="Valor_Neto_${i}"]`);
        const valorNetoSpan = document.getElementById(`valor-neto-span-${i}`);
        const retencionInput = document.getElementById(`retencion-input-${i}`);
        const retencionHidden = document.querySelector(`input[name="Retencion_Fuente_${i}"]`);
        const valorPagadoHidden = document.querySelector(`input[name="Valor_Pagado_${i}"]`);
        const valorPagadoSpan = document.getElementById(`valor-pagado-span-${i}`);

        // Porcentajes
        const porcentajeIVA = parseFloat(document.querySelector(`input[name="Porcentaje_IVA_${i}"]`)?.value) || 0;
        const porcentajeRetencion = parseFloat(document.querySelector(`input[name="Porcentaje_Retencion_${i}"]`)?.value) || 0;

        // Valores actuales
        const horas = parseFloat(horasInput.value) || 0;
        const valorUnitario = parseFloat(valorUnitarioInput.value) || 0;

        // Antes de calcular, si el input está vacío o no es un número, vuelve a modo automático
        if (ivaInput && (ivaInput.value === '' || isNaN(parseFloat(ivaInput.value)))) {
            ivaInput.dataset.manual = 'false';
        }
        if (retencionInput && (retencionInput.value === '' || isNaN(parseFloat(retencionInput.value)))) {
            retencionInput.dataset.manual = 'false';
        }

        // Detectar si IVA o Retención han sido editados manualmente
        const ivaManual = ivaInput && ivaInput.dataset.manual === 'true';
        const retencionManual = retencionInput && retencionInput.dataset.manual === 'true';

        // Cálculos automáticos solo si no han sido editados manualmente
        let iva = ivaManual ? parseFloat(ivaInput.value) : (horas * valorUnitario) * porcentajeIVA / 100;
        if (isNaN(iva)) iva = 0;
        let retencion = retencionManual ? parseFloat(retencionInput.value) : (horas * valorUnitario) * porcentajeRetencion / 100;
        if (isNaN(retencion)) retencion = 0;

        // Cálculos
        const valorCobro = horas * valorUnitario;
        const valorNeto = valorCobro + iva;
        const valorPagado = valorNeto - retencion;

        // Actualizar campos visibles y ocultos
        if (valorCobroSpan) valorCobroSpan.textContent = valorCobro.toFixed(2);
        if (valorCobroHidden) valorCobroHidden.value = valorCobro.toFixed(2);
        if (ivaHidden) ivaHidden.value = iva.toFixed(2);
        if (ivaInput && !ivaManual) ivaInput.value = iva.toFixed(2);
        if (valorNetoSpan) valorNetoSpan.textContent = valorNeto.toFixed(2);
        if (valorNetoHidden) valorNetoHidden.value = valorNeto.toFixed(2);
        if (retencionHidden) retencionHidden.value = retencion.toFixed(2);
        if (retencionInput && !retencionManual) retencionInput.value = retencion.toFixed(2);
        if (valorPagadoSpan) valorPagadoSpan.textContent = valorPagado.toFixed(2);
        if (valorPagadoHidden) valorPagadoHidden.value = valorPagado.toFixed(2);
        
        console.log('Valores actualizados - Valor Neto:', valorNeto.toFixed(2), 'Valor Pagado:', valorPagado.toFixed(2));
    }

    // Evento para marcar IVA y Retención como editados manualmente
    document.querySelectorAll('input[name^="IVA_"], input[name^="Retencion_Fuente_"]').forEach(input => {
        input.addEventListener('input', function () {
            // Si el usuario escribe, marca como manual
            this.dataset.manual = 'true';
            // Si el usuario borra el valor, vuelve a automático
            if (this.value === '') {
                this.dataset.manual = 'false';
            }
            const i = this.name.split('_').pop();
            console.log('Recalculando valores para fila:', i, 'IVA:', this.value);
            recalcularValores(i);
        });
    });

    // Evento para horas y valor unitario: siempre recalcula y solo sobreescribe IVA/Retención si no son manuales
    document.querySelectorAll('input[name^="Cantidad_Horas_"], input[name^="Valor_Unitario_"]').forEach(input => {
        input.addEventListener('input', function () {
            const i = this.name.split('_').pop();
            recalcularValores(i);
        });
    });
});

