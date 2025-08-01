// Habilita el botón de guardado cuando se edita algún campo editable
document.querySelectorAll('input.form-control:not([readonly])').forEach(input => {
    input.addEventListener('input', () => {
        document.getElementById('save-button').disabled = false;
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
});

// Función para guardar todos los registros editados
function saveAllRows() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/facturacion_consultores/guardar/';  // Asegúrate de que la URL sea correcta

    // CSRF token
    const csrf = document.querySelector('input[name=csrfmiddlewaretoken]');
    if (csrf) {
        form.appendChild(csrf.cloneNode());
    }

    // Recolectar todos los campos editados
    document.querySelectorAll('input.form-control, input[type=hidden]').forEach(input => {
        const clone = document.createElement('input');
        clone.type = 'hidden';
        clone.name = input.name;
        clone.value = input.value;
        form.appendChild(clone);
    });

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
    }, 3000);
}

// Mostrar modal al guardar
document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === '1') {
        mostrarModal();
    }

    // 🔽 Nuevo: Controla el botón de eliminar según los checkboxes seleccionados
    const checkboxes = document.querySelectorAll('.row-checkbox');
    const btnEliminar = document.getElementById('delete-button');

    function toggleEliminarButton() {
        const algunoSeleccionado = Array.from(checkboxes).some(cb => cb.checked);
        if (btnEliminar) btnEliminar.disabled = !algunoSeleccionado;
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
            setTimeout(() => location.reload(), 1000);
        } else {
            showMessage('Error al eliminar: ' + (data.error || 'desconocido'), 'danger');
        }
    })
    .catch(error => {
        showMessage('Error en la petición: ' + error.message, 'danger');
    });
    mostrarModal('modaleliminacion');
}
document.addEventListener('DOMContentLoaded', function() {
    // Función para actualizar el panel de resumen
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
            const rowId = this.name.split('_').pop(); // Ej: "Valor_Factura_Cliente_new" -> "new"
            actualizarResumen(rowId);
        });
    });
});
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

