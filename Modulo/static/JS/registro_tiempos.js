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
        if (anio && mes) {
            document.querySelector('#anio-original').textContent = anio;
            document.querySelector('#mes-original').textContent = mes;
            // Guardar los valores en variables globales
            window.originalAnio = anio;
            window.originalMes = mes;
        }
    }

    // Mostrar los valores originales de año y mes en la interfaz
    function displayOriginalAnioMes() {
        const originalAnio = localStorage.getItem('originalAnio');
        const originalMes = localStorage.getItem('originalMes');
        if (originalAnio && originalMes) {
            document.querySelector('#anio-original').textContent = originalAnio;
            document.querySelector('#mes-original').textContent = originalMes;
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

    function saveAllRows() {
        const rows = document.querySelectorAll('tbody tr');
        const data = [];
        const lineasData = {}; // Para acumular totales por línea
        const conceptosData = {}; // Para acumular totales por concepto y línea

        // 1. Recopilar datos de empleados y consultores
        rows.forEach((row) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');
            
            // Datos básicos
            inputs.forEach(input => {
                if (input.name) rowData[input.name] = input.value || null;
            });
    
            // Procesar clientes y conceptos
            const clientes = [];
            const conceptos = [];
            
            // Clientes (Total Operación)
            row.querySelectorAll('input[name^="ClienteId_"]').forEach((input, i) => {
                const clienteId = input.value.trim();
                const tiempoCliente = row.querySelector(`input[name="Tiempo_Clientes_${i + 1}"]`).value.trim() || '0';
                
                clientes.push({
                    cliente: clienteId,
                    tiempo: parseFloat(tiempoCliente)
                });
            });
    
            // Conceptos
            row.querySelectorAll('input[name^="ConceptoId_"]').forEach((input, i) => {
                const conceptoId = input.value.trim();
                const tiempoConcepto = row.querySelector(`input[name="Tiempo_Conceptos_${i + 1}"]`).value.trim() || '0';
                
                // Verificar si las horas son mayores a 0
                if (parseFloat(tiempoConcepto) > 0) {
                    conceptos.push({
                        concepto: conceptoId,
                        tiempo: parseFloat(tiempoConcepto)
                    });
                }
            });
    
            // Acumular totales por línea
            const lineaId = row.querySelector('[name="LineaId"]').value;
            if (!lineasData[lineaId]) {
                lineasData[lineaId] = {
                    horasTrabajadas: 0,
                    horasFacturables: 0,
                    conceptos: {}
                };
            }
    
            // Sumar horas trabajadas (Total Operación)
            lineasData[lineaId].horasTrabajadas += clientes.reduce((acc, curr) => acc + curr.tiempo, 0);
    
            // Sumar conceptos
            conceptos.forEach(({ concepto, tiempo }) => {
                if (!lineasData[lineaId].conceptos[concepto]) {
                    lineasData[lineaId].conceptos[concepto] = 0;
                }
                lineasData[lineaId].conceptos[concepto] += tiempo;
            });
        });
    
        // 2. Procesar Horas Facturables del footer
        document.querySelectorAll('tfoot tr').forEach(row => {
            const lineaId = row.querySelector('[name="LineaId_1"]')?.value; // Ajustar selector según tu HTML
            if (lineaId) {
                const totalFacturable = parseFloat(row.querySelector('[data-total-facturable-linea-row]').textContent) || 0;
                if (lineasData[lineaId]) {
                    lineasData[lineaId].horasFacturables = totalFacturable;
                }
            }
        });
    
        // 3. Estructurar datos para enviar
        Object.keys(lineasData).forEach(lineaId => {
            data.push({
                'type': 'linea',
                'LineaId': lineaId,
                'horasTrabajadas': lineasData[lineaId].horasTrabajadas,
                'horasFacturables': lineasData[lineaId].horasFacturables,
                'Anio': window.originalAnio,
                'Mes': window.originalMes
            });
    
            // Agregar conceptos solo si las horas son mayores a 0
            Object.keys(lineasData[lineaId].conceptos).forEach(conceptoId => {
                const horas = lineasData[lineaId].conceptos[conceptoId];
                if (horas > 0) {
                    data.push({
                        'type': 'concepto',
                        'LineaId': lineaId,
                        'ConceptoId': conceptoId,
                        'horas': horas,
                        'Anio': window.originalAnio,
                        'Mes': window.originalMes
                    });
                }
            });
        });

        rows.forEach((row, index) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');
    
            // Recopilar todos los valores de los inputs en la fila
            inputs.forEach(input => {
                if (input.name) {
                    rowData[input.name] = input.value || null;
                }
            });
    
            // Validar y parsear JSON para los clientes, conceptos y facturables
            try {
                // Crear arrays para los clientes, conceptos y facturables, usando los nombres de los inputs con el índice
                const clientes = [];
                const conceptos = []; 
                const lineaId = row.querySelector('input[name="LineaId"]').value;

                // Recopilar clientes y tiempos
                row.querySelectorAll('input[name^="ClienteId_"]').forEach((input, i) => {
                    const cliente = input.value.trim();
                    const tiempoClienteInput = row.querySelector(`input[name="Tiempo_Clientes_${i + 1}"]`);
                    let tiempoCliente = tiempoClienteInput.value.trim();
                    tiempoCliente = tiempoCliente === '' ? '0' : tiempoCliente; // Si está vacío, asignar '0'
                    const tiempoClienteOriginal = tiempoClienteInput.getAttribute('data-original') || '';
                    if (cliente && tiempoCliente !== tiempoClienteOriginal) {
                        clientes.push({ cliente, tiempoCliente });
                    }
                });

                // Recopilar conceptos y tiempos
                row.querySelectorAll('input[name^="ConceptoId_"]').forEach((input, i) => {
                    const concepto = input.value.trim();
                    const tiempoConceptoInput = row.querySelector(`input[name="Tiempo_Conceptos_${i + 1}"]`);
                    let tiempoConcepto = tiempoConceptoInput.value.trim();
                    tiempoConcepto = tiempoConcepto === '' ? '0' : tiempoConcepto; // Si está vacío, asignar '0'
                    const tiempoConceptoOriginal = tiempoConceptoInput.getAttribute('data-original') || '';
                    if (concepto && tiempoConcepto !== tiempoConceptoOriginal) {
                        conceptos.push({ concepto, tiempoConcepto });
                    }
                });
    
                // Ahora procesamos los clientes, conceptos y facturables
                clientes.forEach(({ cliente, tiempoCliente }) => {
                    data.push({
                        'Documento': rowData.Documento,
                        'ClienteId': cliente,
                        'Tiempo_Clientes': tiempoCliente,
                        'Anio': window.originalAnio,
                        'Mes': window.originalMes,
                        'LineaId': lineaId,
                        'ModuloId': rowData.ModuloId
                    });
                });

                conceptos.forEach(({ concepto, tiempoConcepto }) => {
                    data.push({
                        'Documento': rowData.Documento,
                        'ConceptoId': concepto,
                        'Tiempo_Conceptos': tiempoConcepto,
                        'Anio': window.originalAnio,
                        'Mes': window.originalMes,
                        'LineaId': lineaId
                    });
                });

            } catch (error) {
                console.error(`Error al procesar los datos en la fila ${index + 1}:`, error);
            }
        });

        // Recopilar datos de las líneas facturables en el tfoot
        const tfootRows = document.querySelectorAll('tfoot tr');
        tfootRows.forEach((row, index) => {
            const facturables = [];

            row.querySelectorAll('input[name^="Hora_Facturable_"]').forEach((input, i) => {
                const linea = row.querySelector(`input[name="LineaId_${i + 1}"]`).value.trim();
                const cliente = row.querySelector(`input[name="ClienteId_${i + 1}"]`).value.trim();
                const tiempoFacturableInput = input;
                let tiempoFacturable = tiempoFacturableInput.value.trim();
                tiempoFacturable = tiempoFacturable === '' ? '0' : tiempoFacturable; // Si está vacío, asignar '0'
                const tiempoFacturableOriginal = tiempoFacturableInput.getAttribute('data-original') || '';
                if (linea && cliente && tiempoFacturable !== tiempoFacturableOriginal) {
                    facturables.push({ linea, cliente, tiempoFacturable });
                }
            });

            facturables.forEach(({ linea, cliente, tiempoFacturable }) => {
                data.push({
                    'LineaId': linea,
                    'ClienteId': cliente,
                    'Horas_Facturables': tiempoFacturable,
                    'Anio': window.originalAnio,
                    'Mes': window.originalMes
                });
            });
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
            facturables: {},
            totalClientes: 0,
            totalConceptos: 0,
            totalFacturables: 0,
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
            row.querySelector('td[data-total-clientes-row]').textContent = totalClientesRow.toFixed(2);
            row.querySelector('td[data-total-conceptos-row]').textContent = totalConceptosRow.toFixed(2);
            row.querySelector('td[data-total-horas-row]').textContent = (totalClientesRow + totalConceptosRow).toFixed(2);
            row.querySelector('td[data-dif-horas-row]').textContent = (0).toFixed(2);
        });

        // Recopilar datos de las líneas facturables en el tfoot
        const tfootRows = document.querySelectorAll('tfoot tr');
        tfootRows.forEach(row => {
            let totalFacturablesRow = 0;
            row.querySelectorAll('input[name^="Hora_Facturable_"]').forEach((input, i) => {
                const clienteId = row.querySelector(`input[name="ClienteId_${i + 1}"]`).value;
                const horas = parseFloat(input.value) || 0;
                if (!totals.facturables[clienteId]) {
                    totals.facturables[clienteId] = 0;
                }
                totals.facturables[clienteId] += horas;
                totals.totalFacturables += horas;
                totals.totalHoras += horas;
                totalFacturablesRow += horas;
            });
    
            // Actualizar las columnas de total en la fila actual
            const totalFacturableCell = row.querySelector('td[data-total-facturable-linea-row]');
            if (totalFacturableCell) {
                totalFacturableCell.textContent = totalFacturablesRow.toFixed(2);
            }
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
                    row.querySelector('td[data-dif-horas-row]').textContent = difHorasRow.toFixed(2);
                    totalDifHoras += difHorasRow;
                });

                // Actualizar la columna de diferencia de horas en el pie de página
                document.querySelector('tfoot th[data-dif-horas]').textContent = totalDifHoras.toFixed(2);

                // Actualizar la diferencia de horas para cada colaborador
                rows.forEach(row => {
                    const totalHorasRow = parseFloat(row.querySelector('td[data-total-horas-row]').textContent) || 0;
                    const difHorasRow = horasLaboralesTotales - totalHorasRow;
                    row.querySelector('td[data-dif-horas-row]').textContent = difHorasRow.toFixed(2);
                });
            })
            .catch(error => {
                console.error('Error al obtener los datos de Horas_Habiles:', error);
            });

        // Update the totals in the footer
        document.querySelectorAll('tfoot th[data-cliente-id]').forEach(th => {
            const clienteId = th.getAttribute('data-cliente-id');
            th.textContent = (totals.clientes[clienteId] || 0).toFixed(2);
        });

        document.querySelectorAll('tfoot th[data-concepto-id]').forEach(th => {
            const conceptoId = th.getAttribute('data-concepto-id');
            th.textContent = (totals.conceptos[conceptoId] || 0).toFixed(2);
        });

        document.querySelector('tfoot th[data-total-clientes]').textContent = totals.totalClientes.toFixed(2);
        document.querySelector('tfoot th[data-total-conceptos]').textContent = totals.totalConceptos.toFixed(2);
        document.querySelector('tfoot th[data-total-horas]').textContent = totals.totalHoras.toFixed(2);
    
        // Update the totals for facturables in the footer
        document.querySelectorAll('tfoot th[data-cliente-facturables-id]').forEach(th => {
            const clienteId = th.getAttribute('data-cliente-facturables-id');
            th.textContent = (totals.facturables[clienteId] || 0).toFixed(2);
        });

        document.querySelector('tfoot th[data-total-clientes-facturables]').textContent = totals.totalFacturables.toFixed(2);
        document.querySelector('tfoot th[data-total-horas-facturables]').textContent = totals.totalFacturables.toFixed(2);
    }

    document.querySelectorAll('input[name^="Tiempo_Clientes_"], input[name^="Tiempo_Conceptos_"], input[name^="Hora_Facturable_"]').forEach(input => {
        input.setAttribute('data-original', input.value);
        input.addEventListener('input', recalculateTotals);
    });

    window.saveAllRows = saveAllRows;
    recalculateTotals(); // Initial calculation
});

