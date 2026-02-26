document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Habilitar edición en los detalles seleccionados
    window.enableEditDetails = function () {
        const selected = document.querySelectorAll('.detail-select:checked');
        if (selected.length === 0) {
            showMessage('No has seleccionado ningún detalle para editar.', 'warning');
            return;
        }
        if (selected.length > 1) {
            showMessage('Solo puedes editar un detalle a la vez.', 'warning');
            return;
        }

        const row = selected[0].closest('tr');

        // Lista de campos específicos que son editables
        const editableFields = [
            { name: "Anio", type: "text" },
            { name: "Mes", type: "text" },
            { name: "Valor", type: "text" }
        ];

        // Guardar valores originales en un atributo personalizado
        editableFields.forEach(field => {
            const element = row.querySelector(`[name="${field.name}"]`);
            const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
            if (element) {
                element.setAttribute('data-original-value', element.value);
            }
            if (span) {
                span.setAttribute('data-original-value', span.innerText.trim());
            }
        });

        // Habilitar los campos editables y ocultar los spans correspondientes
        editableFields.forEach(field => {
            const element = row.querySelector(`[name="${field.name}"]`);
            const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
            if (element) {
                element.classList.remove('d-none'); // Mostrar el input
                element.classList.remove('form-control-plaintext');
                element.classList.add('form-control');
                element.readOnly = false; // Habilitar el input
            }
            if (span) {
                span.classList.add('d-none'); // Ocultar el span en modo edición
            }
        });

        // Desactivar todos los checkboxes y botones de edición
        document.getElementById('select-all').disabled = true;
        document.querySelectorAll('.detail-select').forEach(checkbox => checkbox.disabled = true);
        document.getElementById('edit-button').disabled = true;

        // Mostrar botones de "Guardar" y "Cancelar"
        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    };

    // Guardar los cambios en los detalles seleccionados
    window.saveDetails = function () {
        const selected = document.querySelectorAll('.table-primary .detail-select:checked');
        if (selected.length !== 1) {
            showMessage('No hay detalles seleccionados para guardar.', 'warning');
            return;
        }
    
        const row = selected[0].closest('tr');
        const detalleId = row.querySelector('input[name="id"]').value; // Obtener el ID desde el campo oculto
    
        // Verificar si el detalleId es válido
        if (!detalleId) {
            console.error('❌ Error: detalleId no encontrado.');
            showMessage('Error: No se pudo identificar el detalle seleccionado.', 'danger');
            return;
        }
    
        const data = {
            Anio: row.querySelector('input[name="Anio"]').value.trim(),
            Mes: row.querySelector('input[name="Mes"]').value.trim(),
            Valor: parseFloat(row.querySelector('input[name="Valor"]').value.trim()) || 0
        };
        console.log('Datos enviados:', data);
    
        // Cambiar la URL para que coincida con la definida en urls.py
        fetch(`/total_costos_indirectos_editar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ id: detalleId, ...data }) // Enviar el ID junto con los datos
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor.');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                showMessage('Detalles guardados correctamente.', 'success');
                window.location.reload();
            } else {
                showMessage('Error al guardar los detalles: ' + (data.message || 'Error desconocido.'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error al guardar los detalles:', error);
            showMessage('Error al guardar los detalles.', 'danger');
        });
    };

    // Cancelar edición en los detalles seleccionados
    window.cancelEditDetails = function () {
        const selected = document.querySelectorAll('.table-primary .detail-select:checked');
        if (selected.length === 1) {
            const row = selected[0].closest('tr');

            // Restaurar valores originales
            const editableFields = ["Anio", "Mes", "Valor"];
            editableFields.forEach(name => {
                const element = row.querySelector(`[name="${name}"]`);
                const span = row.querySelector(`[data-field="${name}"] span.form-control-plaintext`);
                if (element) {
                    element.value = element.getAttribute('data-original-value');
                    element.classList.add('form-control-plaintext');
                    element.classList.remove('form-control');
                    element.readOnly = true;
                    element.classList.add('d-none'); // Ocultar el input
                }
                if (span) {
                    span.innerText = span.getAttribute('data-original-value');
                    span.classList.remove('d-none'); // Mostrar el span en modo solo lectura
                }
            });

            // Restaurar botones y checkboxes
            document.getElementById('select-all').disabled = false;
            document.querySelectorAll('.detail-select').forEach(checkbox => checkbox.disabled = false);
            document.getElementById('edit-button').disabled = false;

            // Ocultar botones de "Guardar" y "Cancelar"
            document.getElementById('save-button').classList.add('d-none');
            document.getElementById('cancel-button').classList.add('d-none');
        }
    };

// Función para deshabilitar campos después de guardar
    function deshabilitarCampos() {
        const selected = document.querySelectorAll('.table-primary .detail-select:checked');
        selected.forEach(checkbox => {
            const row = checkbox.closest('tr');
            row.querySelectorAll('input, select').forEach(field => {
                field.readOnly = true; // Poner inputs en solo lectura
                field.classList.add('form-control-plaintext');
                field.classList.remove('form-control');
                field.classList.add('d-none'); // Ocultar el campo después de guardar
            });

            // Deshabilitar el select
            const select = row.querySelector('select[name="CostosId"]');
            if (select) {
                select.setAttribute('disabled', true); // Volver a deshabilitar el select
            }

            // Mostrar los spans
            row.querySelectorAll('span.form-control-plaintext').forEach(span => {
                span.classList.remove('d-none');
            });
        });

        // Ocultar el botón de guardar
        document.getElementById('guardar-detalles').classList.add('d-none');
    }

    function showMessage(message, type) {
        const alertBox = document.getElementById('message-box');
        alertBox.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        alertBox.style.display = 'block';
        setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
    }

    

    window.visualizarDetalles = function() {
    let selected = document.querySelectorAll('.row-select:checked');

        if (selected.length !== 1) {
            showMessage('Debes seleccionar un solo elemento para visualizar.', 'danger');
            return;
        }

        let id = selected[0].value;
        document.querySelectorAll('.detail-select').forEach(checkbox => checkbox.checked = false);

        fetch(`/total_costos_indirectos/visualizar/${id}/`)
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
        let costosDisponibles = data.costos_disponibles;

        let tbody = document.getElementById('tabla-detalles-secundaria-tbody');
        tbody.innerHTML = '';

        if (!detalles || detalles.length === 0) {
            document.getElementById('tabla-detalles-container').classList.add('d-none');
            console.warn("⚠ No se encontraron detalles.");
            return;
        }

        detalles.forEach(detalle => {
            // Crear el select para "CostosId" como readonly y con "disabled" para que no sea seleccionable
            let selectCostos = `<select name="CostosId" class="form-control-plaintext" disabled>`;
            costosDisponibles.forEach(costo => {
                let selected = costo.CostoId == detalle.CostosId ? 'selected' : '';
                selectCostos += `<option value="${costo.CostoId}" ${selected}>${costo.Costo}</option>`;
            });
            selectCostos += '</select>';

            let row = `<tr data-id="${detalle.id}">
                <td><input type="checkbox" class="detail-select" value="${detalle.id}"></td>
                <td><input type="text" name="Anio" value="${detalle.Anio}" class="form-control-plaintext" readonly></td>
                <td><input type="text" name="Mes" value="${detalle.Mes}" class="form-control-plaintext" readonly></td>
                <td>${selectCostos}</td>
                <td><input type="text" name="Valor" value="${detalle.Valor}" class="form-control-plaintext detalle-valor" readonly></td>
            </tr>`;
            tbody.innerHTML += row;
        });

        document.getElementById('tabla-detalles-container').classList.remove('d-none');
    }

    window.crearDetalle = function() {
        let selected = document.querySelectorAll('.table-primary .detail-select:checked');

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
        document.querySelectorAll('#tabla-detalles-secundaria-tbody tr').forEach(row => {
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

        // Verificar si estamos en la tabla principal o en la tabla de detalles
        let isInDetailsTable = document.getElementById('tabla-detalles-container').classList.contains('d-none') === false;

        if (isInDetailsTable) {
            // Si estamos en la tabla de detalles, solo eliminar detalles
            document.querySelectorAll("#tabla-detalles-secundaria-tbody .detail-select:checked").forEach((checkbox) => {
                seleccionados.detalles.push(checkbox.value);
            });
        } else {
            // Si estamos en la tabla principal, solo eliminar totales
            document.querySelectorAll(".table-primary .detail-select:checked").forEach((checkbox) => {
                seleccionados.totales.push(checkbox.value);
            });
        }

        // Si no hay elementos seleccionados, no enviar la petición
        if (seleccionados.totales.length === 0 && seleccionados.detalles.length === 0) {
            showMessage("⚠️ No hay elementos seleccionados para eliminar.", "warning");
            return;
        }

        fetch("/total_costos_indirectos/eliminar/", {
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
                    let fila = document.querySelector(`#tabla-detalles-secundaria-tbody tr[data-id='${id}']`);
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

                showMessage("✅ Elemento(s) eliminado(s) correctamente.", "success");
            } else {
                showMessage("⚠️ Error al eliminar: " + data.error, "danger");
            }
        })
        .catch(error => console.error("❌ Error en la petición:", error));
    }

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }



    }
    }
});