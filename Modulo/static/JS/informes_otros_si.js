document.addEventListener('DOMContentLoaded', function () {

    // ===========================================
    // ENVÍO AUTOMÁTICO DEL FORMULARIO SI HAY FILTROS EN LA URL
    // ===========================================
    const urlParams = new URLSearchParams(window.location.search);
    const hasParams = ['Nombre_Cliente', 'Contrato', 'FechaInicio', 'ContratoVigente'].some(param => urlParams.has(param));
    const alreadySubmitted = sessionStorage.getItem('otros_si_autosubmit');

    if (hasParams && !alreadySubmitted) {
        sessionStorage.setItem('otros_si_autosubmit', '1');
        document.getElementById('filtro-otros-si-form').submit();
    } else {
        sessionStorage.removeItem('otros_si_autosubmit');
    }
    
    // ===========================================
    // EVENTO CAMBIO DE CLIENTE: ACTUALIZA CONTRATOS
    // ===========================================
    const clienteSelect = document.getElementById('id_Nombre_Cliente');
    const contratoSelect = document.getElementById('id_Contrato');

    if (!clienteSelect || !contratoSelect) {
        console.warn("⚠️ No se encontraron los campos Cliente o Contrato.");
        return;
    }

    clienteSelect.addEventListener('change', function () {
        const clienteId = this.value;
        console.log("➡️ Cliente seleccionado:", clienteId);
    
        contratoSelect.innerHTML = '<option value="">Cargando contratos...</option>';
    
        if (clienteId) {
            fetch(`/contratos_otros_si/obtener-contratos/${clienteId}/`)
                .then(response => {
                    if (!response.ok) throw new Error("No se pudo obtener los contratos del cliente");
                    return response.json();
                })
                .then(data => {
                    console.log("📦 Contratos recibidos:", data);
                    contratoSelect.innerHTML = '<option value="">Seleccione un contrato</option>';
                    data.contratos.forEach(c => {
                        const option = document.createElement('option');
                        option.value = c.nombre;
                        option.textContent = c.nombre;
                        contratoSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('❌ Error cargando contratos:', error);
                    contratoSelect.innerHTML = '<option value="">Error cargando contratos</option>';
                });
        } else {
            contratoSelect.innerHTML = '<option value="">Seleccione un cliente primero</option>';
        }
    });


    // ===========================================
    // GRÁFICO DE MONEDAS EN MODAL
    // ===========================================
    const cardMonedas = document.getElementById('cardMonedas');
    const modalMonedas = new bootstrap.Modal(document.getElementById('graficoMonedasModal'));

    if (cardMonedas) {
        cardMonedas.addEventListener('click', function () {
            const ctx = document.getElementById('graficoMonedasCanvas').getContext('2d');

            // Destruir gráfico anterior si existe
            if (window.monedaChart) {
                window.monedaChart.destroy();
            }

            // Crear gráfico Doughnut de monedas
            window.monedaChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['USD', 'COP', 'MXN'],
                    datasets: [{
                        label: 'Cantidad de Contratos',
                        data: [
                            parseInt(document.getElementById('graficoMonedasCanvas').dataset.usd) || 0,
                            parseInt(document.getElementById('graficoMonedasCanvas').dataset.cop) || 0,
                            parseInt(document.getElementById('graficoMonedasCanvas').dataset.mxn) || 0
                        ],
                        backgroundColor: ['#0d6efd', '#198754', '#ffc107'],
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.label}: ${ctx.raw}`
                            }
                        }
                    }
                }
            });

            modalMonedas.show();
        });
    }

    // =============================
    // LÓGICA DE REINICIO DE FILTROS
    // =============================
    const resetBtn = document.getElementById('btn-reset-filtros');
    const form = document.querySelector('form');

    if (resetBtn && form) {
        console.log('✔ Botón de reinicio y formulario encontrados');

        resetBtn.addEventListener('click', function () {
        console.log('🔄 Botón de reinicio clickeado');

        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            console.log(`↩ Reiniciando select: ${select.name}`);
            select.value = '';
        });

        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            console.log(`↩ Limpiando input: ${input.name}`);
            input.value = '';
        });
        });
    } else {
        if (!resetBtn) console.error('❌ No se encontró el botón con id="btn-reset-filtros"');
        if (!form) console.error('❌ No se encontró ningún formulario');
    }
    const table = document.getElementById('otrosSiTable');
if (table) {
    const headers = table.querySelectorAll('th.sortable');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-sort');
            const direction = header.getAttribute('data-direction') || 'asc';
            const newDirection = direction === 'asc' ? 'desc' : 'asc';

            sortTableByColumn(table, column, newDirection);

            // Reset all headers to default
            headers.forEach(h => {
                h.setAttribute('data-direction', 'default');
                h.querySelector('.sort-icon-default').style.display = 'inline';
                h.querySelector('.sort-icon-asc').style.display = 'none';
                h.querySelector('.sort-icon-desc').style.display = 'none';
            });
            
            // Set current header direction
            header.setAttribute('data-direction', newDirection);
            header.querySelector('.sort-icon-default').style.display = 'none';
            header.querySelector(`.sort-icon-${newDirection}`).style.display = 'inline';
        });
    });

    function sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Find column index by data-field attribute to be more precise
        const headerCells = Array.from(table.querySelectorAll('thead th'));
        const columnIndex = headerCells.findIndex(th => {
            return th.getAttribute('data-sort') === columnName;
        });
        
        if (columnIndex === -1) return; // Column not found

        rows.sort((a, b) => {
            // Find cells by data-field attribute for more reliable matching
            const cellA = a.querySelector(`td[data-field="${columnName}"]`);
            const cellB = b.querySelector(`td[data-field="${columnName}"]`);
            
            if (!cellA || !cellB) return 0;
            
            // Get the text content, handling different element types
            const getCellText = (cell) => {
                if (cell.querySelector('input, select')) {
                    return cell.querySelector('input, select').value.trim();
                }
                return cell.innerText.trim();
            };
            
            const textA = getCellText(cellA);
            const textB = getCellText(cellB);

            // Numeric comparison
            if (!isNaN(textA) && !isNaN(textB)) {
                return direction === 'asc' ? textA - textB : textB - textA;
            }

            // Date comparison
            if (columnName.includes('fecha') || columnName.includes('fecha')) {
                const dateA = new Date(textA);
                const dateB = new Date(textB);
                if (!isNaN(dateA) && !isNaN(dateB)) {
                    return direction === 'asc' ? dateA - dateB : dateB - dateA;
                }
            }

            // String comparison
            return direction === 'asc' 
                ? textA.localeCompare(textB) 
                : textB.localeCompare(textA);
        });

        // Reattach sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
}      
});
