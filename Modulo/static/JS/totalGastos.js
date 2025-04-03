document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Habilitar edición en los detalles seleccionados
window.enableEditDetails = function() {
    let selected = document.querySelectorAll('.detail-select:checked');
    if (selected.length === 0) {
        alert('No has seleccionado ningún detalle para editar.');
        return;
    }

    selected.forEach(checkbox => {
        let row = checkbox.closest('tr');
        row.querySelectorAll('input, select').forEach(field => {
            field.setAttribute('data-original-value', field.value);
            field.readOnly = false;
            field.classList.remove('form-control-plaintext');
            field.classList.add('form-control');
        });

        // Habilitar el select
        let select = row.querySelector('select[name="GastosId"]');
        if (select) {
            select.removeAttribute('disabled');  // Remover disabled para permitir edición
        }
    });

    document.getElementById('guardar-detalles').classList.remove('d-none');
};

 // Guardar los cambios en los detalles seleccionados
 window.saveDetails = function() {
    let selected = document.querySelectorAll('.detail-select:checked');
    if (selected.length === 0) {
        showMessage('No hay detalles seleccionados para guardar.', 'danger');
        return;
    }

    let details = [];
    let anio = "", mes = "";

    selected.forEach(checkbox => {
        let row = checkbox.closest('tr');
        let detalleId = row.getAttribute("data-id");

        if (!detalleId || detalleId.trim() === "") {
            console.error("❌ ID no válido en fila:", row);
            return;
        }

        let detalle = {
            id: detalleId.trim(),
            Anio: row.querySelector('input[name="Anio"]').value,
            Mes: row.querySelector('input[name="Mes"]').value,
            GastosId_id: row.querySelector('select[name="GastosId"]').value,
            Valor: row.querySelector('input[name="Valor"]').value
        };

        anio = detalle.Anio;  // Guardamos el año para la actualización
        mes = detalle.Mes;    // Guardamos el mes para la actualización

        details.push(detalle);
    });

    fetch('/total_gastos/detalles/editar/', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ detalles: details })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showMessage('Detalles guardados correctamente.', 'success');
            actualizarTotal(anio, mes);  // Llamar a actualizarTotal para recalcular el total
            deshabilitarCampos();  // ✅ Deshabilitar campos después de guardar
        } else {
            showMessage('Error al guardar los detalles.', 'danger');
        }
    })
    .catch(error => {
        console.error('❌ Error al guardar detalles:', error);
        showMessage('Error al guardar los detalles.', 'danger');
    });
};

// Función para deshabilitar campos después de guardar
function deshabilitarCampos() {
    let selected = document.querySelectorAll('.detail-select:checked');
    selected.forEach(checkbox => {
        let row = checkbox.closest('tr');
        row.querySelectorAll('input, select').forEach(field => {
            field.readOnly = true;  // Poner inputs en solo lectura
            field.classList.add('form-control-plaintext');
            field.classList.remove('form-control');
        });

        // Deshabilitar el select
        let select = row.querySelector('select[name="GastosId"]');
        if (select) {
            select.setAttribute('disabled', true);  // Volver a deshabilitar el select
        }
    });

    // Ocultar el botón de guardar
    document.getElementById('guardar-detalles').classList.add('d-none');
}

window.cancelEditDetails = function() {
    let selected = document.querySelectorAll('.detail-select:checked');
    selected.forEach(checkbox => {
        let row = checkbox.closest('tr');
        row.querySelectorAll('input').forEach(input => {
            if (input.hasAttribute('data-original-value')) {
                input.value = input.getAttribute('data-original-value');  // Restaurar valores originales
            }
            input.readOnly = true;
            input.classList.add('form-control-plaintext');
            input.classList.remove('form-control');
        });
        checkbox.checked = false;  // Desmarcar los checkboxes
    });

    document.getElementById('guardar-detalles').classList.add('d-none');  // Ocultar botón de guardar
};

function showMessage(message, type) {
    const alertBox = document.getElementById('message-box');
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type} alert-dismissible fade show`;
    alertBox.style.display = 'block';
    setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
}
});

window.visualizarDetalles = function() {
    let selected = document.querySelectorAll('.row-select:checked');

    if (selected.length !== 1) {
        showMessage('Debes seleccionar un solo elemento para visualizar.', 'danger');
        return;
    }

    let id = selected[0].value;
    document.querySelectorAll('.row-select').forEach(checkbox => checkbox.checked = false);

    fetch(`/total_gastos/visualizar/${id}/`)
        .then(response => response.json())
        .then(data => {
            actualizarTablaDetalles(data);
        })
        .catch(error => {
            console.error('❌ Error al obtener los detalles:', error);
            showMessage('Error al cargar los detalles.', 'danger');
        });
};

// Función para actualizar la tabla con los detalles
function actualizarTablaDetalles(data) {
    let detalles = data.detalles;
    let gastosDisponibles = data.gastos_disponibles;

    let tbody = document.getElementById('tabla-detalles-tbody');
    tbody.innerHTML = '';

    if (!detalles || detalles.length === 0) {
        document.getElementById('tabla-detalles-container').classList.add('d-none');
        console.warn("⚠ No se encontraron detalles.");
        return;
    }

    detalles.forEach(detalle => {
        // Crear el select para "CostosId" como readonly y con "disabled" para que no sea seleccionable
        let selectGastos = `<select name="GastosId" class="form-control-plaintext" disabled>`;
        gastosDisponibles.forEach(gasto => {
            let selected = gasto.GastoId == detalle.GastosId ? 'selected' : '';
            selectGastos += `<option value="${gasto.GastoId}" ${selected}>${gasto.Gasto}</option>`;
        });
        selectGastos += '</select>';

        let row = `<tr data-id="${detalle.id}">
            <td><input type="checkbox" class="detail-select" value="${detalle.id}"></td>
            <td><input type="text" name="Anio" value="${detalle.Anio}" class="form-control-plaintext" readonly></td>
            <td><input type="text" name="Mes" value="${detalle.Mes}" class="form-control-plaintext" readonly></td>
            <td>${selectGastos}</td>
            <td><input type="text" name="Valor" value="${detalle.Valor}" class="form-control-plaintext detalle-valor" readonly></td>
        </tr>`;
        tbody.innerHTML += row;
    });

    document.getElementById('tabla-detalles-container').classList.remove('d-none');
}

window.crearDetalle = function() {
    let selected = document.querySelectorAll('.row-select:checked');

    if (selected.length !== 1) {
        showMessage('Debes seleccionar un solo elemento para agregar un detalle.', 'danger');
        return;
    }

    let row = selected[0].closest('tr');
    let anio = row.getAttribute('data-anio');
    let mes = row.getAttribute('data-mes');

    if (!anio || !mes) {
        showMessage('No se pudo obtener el Año y Mes.', 'danger');
        return;
    }

    // Mostrar modal o formulario para ingresar solo "Costo" y "Valor"
    document.getElementById('detalle-anio').value = anio;
    document.getElementById('detalle-mes').value = mes;
    document.getElementById('modal-crear-detalle').classList.remove('d-none');

    actualizarTotal(anio, mes);
};

function actualizarTotal(anio, mes) {
    // Primero, seleccionamos todas las filas de la tabla de detalles
    let total = 0;
    document.querySelectorAll('#tabla-detalles-tbody tr').forEach(row => {
        let rowAnio = row.querySelector('input[name="Anio"]').value;
        let rowMes = row.querySelector('input[name="Mes"]').value;

        // Si la fila corresponde al año y mes seleccionados, sumamos el valor
        if (rowAnio === anio && rowMes === mes) {
            let valor = parseFloat(row.querySelector('input[name="Valor"]').value) || 0;
            total += valor;  // Sumar el valor de la fila
        }
    });

    // Ahora actualizamos el total en la tabla principal
    let totalCell = document.querySelector(`#total-${anio}-${mes}`);
    if (totalCell) {
        totalCell.textContent = total.toFixed(2);  // Actualizamos el total con dos decimales
    }
}
function eliminarSeleccionados(event) {
    event.preventDefault();  // Evita el envío del formulario por defecto

    let seleccionados = {
        totales: [],
        detalles: []
    };

    document.querySelectorAll(".row-select:checked").forEach((checkbox) => {
        seleccionados.totales.push(checkbox.value);
    });

    document.querySelectorAll(".detail-select:checked").forEach((checkbox) => {
        seleccionados.detalles.push(checkbox.value);
    });

    // Si no hay elementos seleccionados, no enviar la petición
    if (seleccionados.totales.length === 0 && seleccionados.detalles.length === 0) {
        alert("⚠️ No hay elementos seleccionados para eliminar.");
        return;
    }

    fetch("/total_gastos/eliminar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(seleccionados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let anio = "", mes = "";

            // Eliminar filas seleccionadas de la tabla
            seleccionados.detalles.forEach((id) => {
                let fila = document.querySelector(`tr[data-id='${id}']`);
                if (fila) {
                    anio = fila.querySelector('input[name="Anio"]').value;
                    mes = fila.querySelector('input[name="Mes"]').value;
                    fila.remove();
                }
            });

            seleccionados.totales.forEach((id) => {
                let fila = document.querySelector(`#row-${id}`);
                if (fila) fila.remove();
            });

            // Llamar a actualizarTotal solo si tenemos el año y mes
            if (anio && mes) {
                actualizarTotal(anio, mes);
            }

            alert("✅ Elemento(s) eliminado(s) correctamente.");
        } else {
            alert("⚠️ Error al eliminar: " + data.error);
        }
    })
    .catch(error => console.error("❌ Error en la petición:", error));
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
