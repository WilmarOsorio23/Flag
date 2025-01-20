document.addEventListener('DOMContentLoaded', function () {
    // Obtener el valor del token CSRF para ser utilizado en las solicitudes POST
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Inhabilitar la tecla Enter para evitar que envíen formularios accidentalmente
    preventFormSubmissionOnEnter();

    // Funciones reutilizables

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

    function saveAllRows() {
        const rows = document.querySelectorAll('tbody tr');
        const data = [];
        // Obtener el año y el mes del filtro
        const anio = document.querySelector('select[name="Anio"]').value;
        const mes = document.querySelector('select[name="Mes"]').value;
    
        rows.forEach((row, index) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');
    
            // Recopilar todos los valores de los inputs en la fila
            inputs.forEach(input => {
                if (input.name) {
                    rowData[input.name] = input.value || null;
                }
            });
    
            // Validar y parsear JSON para los clientes y conceptos
            try {
                // Crear arrays para los clientes y conceptos, usando los nombres de los inputs con el índice
                const clientes = [];
                const conceptos = [];
    
                // Recopilar clientes y tiempos
                row.querySelectorAll('input[name^="ClienteId_"]').forEach((input, i) => {
                    const cliente = input.value.trim();
                    const tiempoCliente = row.querySelector(`input[name="Tiempo_Clientes_${i + 1}"]`).value.trim();
                    if (cliente && tiempoCliente) {
                        clientes.push({ cliente, tiempoCliente });
                    }
                });
    
                // Recopilar conceptos y tiempos
                row.querySelectorAll('input[name^="ConceptoId_"]').forEach((input, i) => {
                    const concepto = input.value.trim();
                    const tiempoConcepto = row.querySelector(`input[name="Tiempo_Conceptos_${i + 1}"]`).value.trim();
                    if (concepto && tiempoConcepto) {
                        conceptos.push({ concepto, tiempoConcepto });
                    }
                });
    
                // Ahora procesamos los clientes y conceptos
                clientes.forEach(({ cliente, tiempoCliente }) => {
                    data.push({
                        'Documento': rowData.Documento,
                        'ClienteId': cliente,
                        'Tiempo_Clientes': tiempoCliente,
                        'Anio': anio,
                        'Mes': mes
                    });
                });

                conceptos.forEach(({ concepto, tiempoConcepto }) => {
                    data.push({
                        'Documento': rowData.Documento,
                        'ConceptoId': concepto,
                        'Tiempo_Conceptos': tiempoConcepto,
                        'Anio': anio,
                        'Mes': mes
                    });
                });

            } catch (error) {
                console.error(`Error al procesar los datos en la fila ${index + 1}:`, error);
            }
        });

        showSavingMessage(true);
    
        // Realizar la petición para guardar los datos
        fetch('/registro_tiempos/guardar/', {
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
            clientes: {},
            conceptos: {},
            totalClientes: 0,
            totalConceptos: 0,
            totalHoras: 0,
            difHoras: 0
        };

        rows.forEach(row => {
            let totalClientesRow = 0;
            let totalConceptosRow = 0;

            row.querySelectorAll('input[name^="Tiempo_Clientes_"]').forEach((input, i) => {
                const clienteId = row.querySelector(`input[name="ClienteId_${i + 1}"]`).value;
                const horas = parseFloat(input.value) || 0;
                if (!totals.clientes[clienteId]) {
                    totals.clientes[clienteId] = 0;
                }
                totals.clientes[clienteId] += horas;
                totals.totalClientes += horas;
                totals.totalHoras += horas;
                totalClientesRow += horas;
            });

            row.querySelectorAll('input[name^="Tiempo_Conceptos_"]').forEach((input, i) => {
                const conceptoId = row.querySelector(`input[name="ConceptoId_${i + 1}"]`).value;
                const horas = parseFloat(input.value) || 0;
                if (!totals.conceptos[conceptoId]) {
                    totals.conceptos[conceptoId] = 0;
                }
                totals.conceptos[conceptoId] += horas;
                totals.totalConceptos += horas;
                totals.totalHoras += horas;
                totalConceptosRow += horas;
            });

            // Actualizar las columnas de total en la fila actual
            row.querySelector('td[data-total-clientes-row]').textContent = totalClientesRow.toFixed(0);
            row.querySelector('td[data-total-conceptos-row]').textContent = totalConceptosRow.toFixed(0);
            row.querySelector('td[data-total-horas-row]').textContent = (totalClientesRow + totalConceptosRow).toFixed(0);
            row.querySelector('td[data-dif-horas-row]').textContent = (0).toFixed(0);
        });

        // Obtener el año y el mes del filtro
        const anio = document.querySelector('select[name="Anio"]').value;
        const mes = document.querySelector('select[name="Mes"]').value;

        // Obtener los datos de Horas_Habiles
        fetch(`/registro_tiempos/horas_habiles/?anio=${anio}&mes=${mes}`)
            .then(response => response.json())
            .then(data => {
                const diasHabiles = data.Dias_Habiles;
                const horasLaborales = data.Horas_Laborales;

                // Calcular las horas laborales totales del mes
                const horasLaboralesTotales = diasHabiles * horasLaborales;

                // Actualizar los valores en el HTML
                document.querySelector('#dias-habiles').textContent = diasHabiles;
                document.querySelector('#horas-habiles').textContent = horasLaboralesTotales;

                // Calcular la diferencia de horas
                let totalDifHoras = 0;
                rows.forEach(row => {
                    const totalHorasRow = parseFloat(row.querySelector('td[data-total-horas-row]').textContent) || 0;
                    const difHorasRow = horasLaboralesTotales - totalHorasRow;
                    row.querySelector('td[data-dif-horas-row]').textContent = difHorasRow.toFixed(0);
                    totalDifHoras += difHorasRow;
                });

                // Actualizar la columna de diferencia de horas en el pie de página
                document.querySelector('tfoot th[data-dif-horas]').textContent = totalDifHoras.toFixed(0);

                // Actualizar la diferencia de horas para cada colaborador
                rows.forEach(row => {
                    const totalHorasRow = parseFloat(row.querySelector('td[data-total-horas-row]').textContent) || 0;
                    const difHorasRow = horasLaboralesTotales - totalHorasRow;
                    row.querySelector('td[data-dif-horas-row]').textContent = difHorasRow.toFixed(0);
                });
            })
            .catch(error => {
                console.error('Error al obtener los datos de Horas_Habiles:', error);
            });

        // Update the totals in the footer
        document.querySelectorAll('tfoot th[data-cliente-id]').forEach(th => {
            const clienteId = th.getAttribute('data-cliente-id');
            th.textContent = (totals.clientes[clienteId] || 0).toFixed(0);
        });

        document.querySelectorAll('tfoot th[data-concepto-id]').forEach(th => {
            const conceptoId = th.getAttribute('data-concepto-id');
            th.textContent = (totals.conceptos[conceptoId] || 0).toFixed(0);
        });

        document.querySelector('tfoot th[data-total-clientes]').textContent = totals.totalClientes.toFixed(0);
        document.querySelector('tfoot th[data-total-conceptos]').textContent = totals.totalConceptos.toFixed(0);
        document.querySelector('tfoot th[data-total-horas]').textContent = totals.totalHoras.toFixed(0);
    }

    document.querySelectorAll('input[name^="Tiempo_Clientes_"], input[name^="Tiempo_Conceptos_"]').forEach(input => {
        input.addEventListener('input', recalculateTotals);
    });

    window.saveAllRows = saveAllRows;
    recalculateTotals(); // Initial calculation
});

