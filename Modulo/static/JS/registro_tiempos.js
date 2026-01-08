document.addEventListener('DOMContentLoaded', function () {
    // CSRF seguro
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfInput ? csrfInput.value : '';

    // Cache de horas hábiles para no hacer fetch en cada keypress
    let horasHabilesCache = {
        anio: null,
        mes: null,
        diasHabiles: null,
        horasLaborales: null,
        horasLaboralesTotales: null,
    };

    // Timer para hacer debounce de recálculo de totales
    let recalcTimeout = null;

    // Recuperar año/mes desde la URL y exponer globalmente
    updateAnioMesFromURL();

    // Bloquear Enter para evitar submits accidentales
    preventFormSubmissionOnEnter();

    // --------------------- Helpers ---------------------

    function updateAnioMesFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const anio = urlParams.get('Anio');
        const mes = urlParams.get('Mes');
        if (anio && mes) {
            const anioEl = document.querySelector('#anio-original');
            const mesEl = document.querySelector('#mes-original');
            if (anioEl) anioEl.textContent = anio;
            if (mesEl) mesEl.textContent = mes;
            window.originalAnio = anio;
            window.originalMes = mes;
        }
    }

    function preventFormSubmissionOnEnter() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        });
    }

    // Helpers de mensajes (unificados)
    function showInfo(msg) { return window.showMessage ? window.showMessage(msg, 'info') : alert(msg); }
    function showOk(msg) { return window.showSuccess ? window.showSuccess(msg) : (window.showMessage ? window.showMessage(msg, 'success') : alert(msg)); }
    function showWarn(msg) { return window.showWarning ? window.showWarning(msg) : (window.showMessage ? window.showMessage(msg, 'warning') : alert(msg)); }
    function showErr(msg) { return window.showError ? window.showError(msg) : (window.showMessage ? window.showMessage(msg, 'danger') : alert(msg)); }

    // UI de guardado: spinner en el botón + mensaje flotante
    function startSavingUI() {
        const btn = document.getElementById('save-button');
        let toast = null;

        if (btn) {
            btn.disabled = true;
            btn.dataset.originalHtml = btn.innerHTML;
            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Guardando...
            `;
        }

        // Mostrar mensaje flotante (sistema unificado)
        if (window.showFloatingMessage) {
            toast = window.showFloatingMessage('Guardando...', 'info');
        } else if (window.showMessage) {
            toast = window.showMessage('Guardando...', 'info');
        }

        function stop(resultType = null, resultMessage = null) {
            // Ocultar toast si existe
            try {
                if (toast && typeof window.hideMessage === 'function') {
                    window.hideMessage(toast);
                } else if (toast && toast.remove) {
                    toast.remove();
                }
            } catch (e) {
                console.error('Error ocultando mensaje:', e);
            }

            // Restaurar botón
            if (btn) {
                btn.disabled = false;
                if (btn.dataset.originalHtml) btn.innerHTML = btn.dataset.originalHtml;
            }

            // Mostrar resultado final
            if (resultMessage) {
                if (resultType === 'success') showOk(resultMessage);
                else if (resultType === 'warning') showWarn(resultMessage);
                else if (resultType === 'danger' || resultType === 'error') showErr(resultMessage);
                else showInfo(resultMessage);
            }
        }

        return { stop };
    }

    // --------------------- Guardado ---------------------

    function saveAllRows() {
        // Validación de contexto (Anio/Mes)
        if (!window.originalAnio || !window.originalMes) {
            showWarn('Falta Año/Mes en los filtros. Usa "Buscar" antes de guardar.');
            return;
        }

        const rows = document.querySelectorAll('tbody tr');
        const data = [];
        const lineasData = {}; // totales por línea

        // 1) Recopilar datos por fila + acumular por línea
        rows.forEach((row) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');

            inputs.forEach(input => {
                if (input.name) rowData[input.name] = input.value || null;
            });

            const clientes = [];
            const conceptos = [];

            // Clientes (operación)
            row.querySelectorAll('input[name^="ClienteId_"]').forEach((input, i) => {
                const clienteId = (input.value || '').trim();
                const tiempoClienteEl = row.querySelector(`input[name="Tiempo_Clientes_${i + 1}"]`);
                const tiempoCliente = tiempoClienteEl ? (tiempoClienteEl.value || '0').trim() : '0';
                clientes.push({
                    cliente: clienteId,
                    tiempo: parseFloat(tiempoCliente || '0')
                });
            });

            // Conceptos
            row.querySelectorAll('input[name^="ConceptoId_"]').forEach((input, i) => {
                const conceptoId = (input.value || '').trim();
                const tiempoConceptoEl = row.querySelector(`input[name="Tiempo_Conceptos_${i + 1}"]`);
                const tiempoConcepto = tiempoConceptoEl ? (tiempoConceptoEl.value || '0').trim() : '0';
                const num = parseFloat(tiempoConcepto || '0');
                if (num > 0) {
                    conceptos.push({ concepto: conceptoId, tiempo: num });
                }
            });

            const lineaIdInput = row.querySelector('[name="LineaId"]');
            const lineaId = lineaIdInput ? lineaIdInput.value : null;
            if (!lineaId) return;

            if (!lineasData[lineaId]) {
                lineasData[lineaId] = {
                    horasTrabajadas: 0,
                    horasFacturables: 0,
                    conceptos: {}
                };
            }

            lineasData[lineaId].horasTrabajadas += clientes.reduce((acc, c) => acc + (c.tiempo || 0), 0);

            conceptos.forEach(({ concepto, tiempo }) => {
                if (!lineasData[lineaId].conceptos[concepto]) {
                    lineasData[lineaId].conceptos[concepto] = 0;
                }
                lineasData[lineaId].conceptos[concepto] += tiempo;
            });
        });

        // 2) Procesar horas facturables (tfoot)
        document.querySelectorAll('tfoot tr').forEach(row => {
            const lineaId = row.querySelector('[name="LineaId_1"]')?.value;
            if (lineaId) {
                const totalFacturableCell = row.querySelector('[data-total-facturable-linea-row]');
                const totalFacturable = totalFacturableCell ? parseFloat(totalFacturableCell.textContent || '0') : 0;
                if (lineasData[lineaId]) {
                    lineasData[lineaId].horasFacturables = totalFacturable;
                }
            }
        });

        // 3) Estructurar totales de línea y conceptos por línea
        Object.keys(lineasData).forEach(lineaId => {
            data.push({
                type: 'linea',
                LineaId: lineaId,
                horasTrabajadas: lineasData[lineaId].horasTrabajadas,
                horasFacturables: lineasData[lineaId].horasFacturables,
                Anio: window.originalAnio,
                Mes: window.originalMes
            });

            Object.keys(lineasData[lineaId].conceptos).forEach(conceptoId => {
                const horas = lineasData[lineaId].conceptos[conceptoId];
                if (horas > 0) {
                    data.push({
                        type: 'concepto',
                        LineaId: lineaId,
                        ConceptoId: conceptoId,
                        horas: horas,
                        Anio: window.originalAnio,
                        Mes: window.originalMes
                    });
                }
            });
        });

        // 4) Cambios por fila (solo cuando difieren de data-original)
        rows.forEach((row, index) => {
            const rowData = {};
            const inputs = row.querySelectorAll('input');

            inputs.forEach(input => {
                if (input.name) rowData[input.name] = input.value || null;
            });

            try {
                const clientes = [];
                const conceptos = [];
                const lineaIdEl = row.querySelector('input[name="LineaId"]');
                const lineaId = lineaIdEl ? lineaIdEl.value : null;

                row.querySelectorAll('input[name^="ClienteId_"]').forEach((input, i) => {
                    const cliente = (input.value || '').trim();
                    const tiempoClienteInput = row.querySelector(`input[name="Tiempo_Clientes_${i + 1}"]`);
                    if (!tiempoClienteInput) return;
                    let tiempoCliente = (tiempoClienteInput.value || '').trim();
                    tiempoCliente = tiempoCliente === '' ? '0' : tiempoCliente;
                    const original = tiempoClienteInput.getAttribute('data-original') || '';
                    if (cliente && tiempoCliente !== original) {
                        clientes.push({ cliente, tiempoCliente });
                    }
                });

                row.querySelectorAll('input[name^="ConceptoId_"]').forEach((input, i) => {
                    const concepto = (input.value || '').trim();
                    const tiempoConceptoInput = row.querySelector(`input[name="Tiempo_Conceptos_${i + 1}"]`);
                    if (!tiempoConceptoInput) return;
                    let tiempoConcepto = (tiempoConceptoInput.value || '').trim();
                    tiempoConcepto = tiempoConcepto === '' ? '0' : tiempoConcepto;
                    const original = tiempoConceptoInput.getAttribute('data-original') || '';
                    if (concepto && tiempoConcepto !== original) {
                        conceptos.push({ concepto, tiempoConcepto });
                    }
                });

                clientes.forEach(({ cliente, tiempoCliente }) => {
                    data.push({
                        Documento: rowData.Documento,
                        ClienteId: cliente,
                        Tiempo_Clientes: tiempoCliente,
                        Anio: window.originalAnio,
                        Mes: window.originalMes,
                        LineaId: lineaId,
                        ModuloId: rowData.ModuloId
                    });
                });

                conceptos.forEach(({ concepto, tiempoConcepto }) => {
                    data.push({
                        Documento: rowData.Documento,
                        ConceptoId: concepto,
                        Tiempo_Conceptos: tiempoConcepto,
                        Anio: window.originalAnio,
                        Mes: window.originalMes,
                        LineaId: lineaId
                    });
                });

            } catch (error) {
                console.error(`Error al procesar los datos en la fila ${index + 1}:`, error);
            }
        });

        // 5) Facturables (tfoot) — enviar solo cambios
        const tfootRows = document.querySelectorAll('tfoot tr');
        tfootRows.forEach(row => {
            const facturables = [];

            row.querySelectorAll('input[name^="Hora_Facturable_"]').forEach((input, i) => {
                const lineaEl = row.querySelector(`input[name="LineaId_${i + 1}"]`);
                const clienteEl = row.querySelector(`input[name="ClienteId_${i + 1}"]`);
                if (!lineaEl || !clienteEl) return;

                const linea = (lineaEl.value || '').trim();
                const cliente = (clienteEl.value || '').trim();
                let tiempo = (input.value || '').trim();
                tiempo = tiempo === '' ? '0' : tiempo;
                const original = input.getAttribute('data-original') || '';
                if (linea && cliente && tiempo !== original) {
                    facturables.push({ linea, cliente, tiempoFacturable: tiempo });
                }
            });

            facturables.forEach(({ linea, cliente, tiempoFacturable }) => {
                data.push({
                    LineaId: linea,
                    ClienteId: cliente,
                    Horas_Facturables: tiempoFacturable,
                    Anio: window.originalAnio,
                    Mes: window.originalMes
                });
            });
        });

        const saving = startSavingUI();

        fetch('/registro_tiempos/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ data })
        })
            .then(r => r.json())
            .then(result => {
                if (result.status === 'success') {
                    saving.stop('success', 'Datos guardados correctamente.');

                    // Actualizar data-original con los nuevos valores
                    document.querySelectorAll('input[name^="Tiempo_Clientes_"], input[name^="Tiempo_Conceptos_"], input[name^="Hora_Facturable_"]').forEach(input => {
                        input.setAttribute('data-original', input.value);
                    });
                } else {
                    saving.stop('danger', result.error ? `Error: ${result.error}` : 'Error al guardar los datos.');
                }
            })
            .catch(err => {
                console.error('Error:', err);
                saving.stop('danger', 'Error de conexión al guardar los datos.');
            });
    }

    // --------------------- Recalcular totales ---------------------

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
                const clienteIdEl = row.querySelector(`input[name="ClienteId_${i + 1}"]`);
                const clienteId = clienteIdEl ? clienteIdEl.value : '';
                const horas = parseFloat(input.value) || 0;
                if (!totals.clientes[clienteId]) totals.clientes[clienteId] = 0;
                totals.clientes[clienteId] += horas;
                totals.totalClientes += horas;
                totals.totalHoras += horas;
                totalClientesRow += horas;
            });

            row.querySelectorAll('input[name^="Tiempo_Conceptos_"]').forEach((input, i) => {
                const conceptoIdEl = row.querySelector(`input[name="ConceptoId_${i + 1}"]`);
                const conceptoId = conceptoIdEl ? conceptoIdEl.value : '';
                const horas = parseFloat(input.value) || 0;
                if (!totals.conceptos[conceptoId]) totals.conceptos[conceptoId] = 0;
                totals.conceptos[conceptoId] += horas;
                totals.totalConceptos += horas;
                totals.totalHoras += horas;
                totalConceptosRow += horas;
            });

            const tc = row.querySelector('td[data-total-clientes-row]');
            const tco = row.querySelector('td[data-total-conceptos-row]');
            const th = row.querySelector('td[data-total-horas-row]');
            const dif = row.querySelector('td[data-dif-horas-row]');
            const totalHorasRow = totalClientesRow + totalConceptosRow;

            if (tc) tc.textContent = totalClientesRow.toFixed(2);
            if (tco) tco.textContent = totalConceptosRow.toFixed(2);
            if (th) th.textContent = totalHorasRow.toFixed(2);
            if (dif) dif.textContent = (0).toFixed(2);
        });

        const tfootRows = document.querySelectorAll('tfoot tr');
        tfootRows.forEach(row => {
            let totalFacturablesRow = 0;
            row.querySelectorAll('input[name^="Hora_Facturable_"]').forEach((input, i) => {
                const clienteIdEl = row.querySelector(`input[name="ClienteId_${i + 1}"]`);
                const clienteId = clienteIdEl ? clienteIdEl.value : '';
                const horas = parseFloat(input.value) || 0;
                if (!totals.facturables[clienteId]) totals.facturables[clienteId] = 0;
                totals.facturables[clienteId] += horas;
                totals.totalFacturables += horas;
                totals.totalHoras += horas;
                totalFacturablesRow += horas;
            });

            const totalFacturableCell = row.querySelector('td[data-total-facturable-linea-row]');
            if (totalFacturableCell) totalFacturableCell.textContent = totalFacturablesRow.toFixed(2);
        });

        const anioSel = document.querySelector('select[name="Anio"]');
        const mesSel = document.querySelector('select[name="Mes"]');
        const anio = anioSel ? anioSel.value : (window.originalAnio || '');
        const mes = mesSel ? mesSel.value : (window.originalMes || '');

        const applyHorasHabiles = (diasHabiles, horasLaborales) => {
            const dias = diasHabiles || 0;
            const horas = horasLaborales || 0;
            const horasLaboralesTotales = dias * horas;

            const diasEl = document.querySelector('#dias-habiles');
            const hlEl = document.querySelector('#horas-habiles');
            if (diasEl) diasEl.textContent = dias;
            if (hlEl) hlEl.textContent = horasLaboralesTotales;

            let totalDifHoras = 0;
            rows.forEach(row => {
                const th = row.querySelector('td[data-total-horas-row]');
                const dif = row.querySelector('td[data-dif-horas-row]');
                const totalHorasRow = th ? parseFloat(th.textContent) || 0 : 0;
                const difHorasRow = horasLaboralesTotales - totalHorasRow;
                if (dif) dif.textContent = difHorasRow.toFixed(2);
                totalDifHoras += difHorasRow;
            });

            const difFooter = document.querySelector('tfoot th[data-dif-horas]');
            if (difFooter) difFooter.textContent = totalDifHoras.toFixed(2);
        };

        if (!anio || !mes) {
            updateFooterTotals(totals);
            return;
        }

        if (
            horasHabilesCache.anio === anio &&
            horasHabilesCache.mes === mes &&
            horasHabilesCache.diasHabiles !== null &&
            horasHabilesCache.horasLaborales !== null
        ) {
            applyHorasHabiles(horasHabilesCache.diasHabiles, horasHabilesCache.horasLaborales);
            updateFooterTotals(totals);
            return;
        }

        fetch(`/registro_tiempos/horas_habiles/?anio=${anio}&mes=${mes}`)
            .then(response => response.json())
            .then(data => {
                const diasHabiles = data.Dias_Habiles || 0;
                const horasLaborales = data.Horas_Laborales || 0;

                horasHabilesCache = {
                    anio,
                    mes,
                    diasHabiles,
                    horasLaborales,
                    horasLaboralesTotales: diasHabiles * horasLaborales
                };

                applyHorasHabiles(diasHabiles, horasLaborales);
                updateFooterTotals(totals);
            })
            .catch(error => {
                console.error('Error al obtener los datos de Horas_Habiles:', error);
                updateFooterTotals(totals);
            });
    }

    function updateFooterTotals(totals) {
        document.querySelectorAll('tfoot th[data-cliente-id]').forEach(th => {
            const clienteId = th.getAttribute('data-cliente-id');
            th.textContent = (totals.clientes[clienteId] || 0).toFixed(2);
        });

        document.querySelectorAll('tfoot th[data-concepto-id]').forEach(th => {
            const conceptoId = th.getAttribute('data-concepto-id');
            th.textContent = (totals.conceptos[conceptoId] || 0).toFixed(2);
        });

        const tc = document.querySelector('tfoot th[data-total-clientes]');
        const tco = document.querySelector('tfoot th[data-total-conceptos]');
        const th = document.querySelector('tfoot th[data-total-horas]');
        if (tc) tc.textContent = totals.totalClientes.toFixed(2);
        if (tco) tco.textContent = totals.totalConceptos.toFixed(2);
        if (th) th.textContent = totals.totalHoras.toFixed(2);
    }

    // --------------------- Listeners ---------------------

    function onTotalsInputChange() {
        if (recalcTimeout) clearTimeout(recalcTimeout);
        recalcTimeout = setTimeout(recalculateTotals, 200);
    }

    document.querySelectorAll(
        'input[name^="Tiempo_Clientes_"], input[name^="Tiempo_Conceptos_"], input[name^="Hora_Facturable_"]'
    ).forEach(input => {
        input.setAttribute('data-original', input.value);
        input.addEventListener('input', onTotalsInputChange);
    });

    const anioSel = document.querySelector('select[name="Anio"]');
    const mesSel = document.querySelector('select[name="Mes"]');
    [anioSel, mesSel].forEach(sel => {
        if (!sel) return;
        sel.addEventListener('change', () => {
            horasHabilesCache = {
                anio: null,
                mes: null,
                diasHabiles: null,
                horasLaborales: null,
                horasLaboralesTotales: null,
            };
        });
    });

    // Exponer función global para usarla en el botón "Guardar"
    window.saveAllRows = saveAllRows;

    // Cálculo inicial
    recalculateTotals();
});
