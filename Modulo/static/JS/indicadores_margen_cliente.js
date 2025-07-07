document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tabs
    const triggerTabList = [].slice.call(document.querySelectorAll('#myTab button'))
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl)
        triggerEl.addEventListener('click', event => {
            event.preventDefault()
            tabTrigger.show()
            
            // Renderizar gráfico si se hace clic en la pestaña de gráficas
            if (triggerEl.id === 'graficas-tab') {
                setTimeout(renderMargenClienteChart, 100);
            }
        })
    })
    
    // Actualiza el texto del dropdown al seleccionar/desmarcar opciones
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.nextSibling.textContent.trim());
        
        button.textContent = selectedOptions.length > 0
            ? selectedOptions.join(', ')    
            : selectedText;
    }

    // Meses
    const mesCheckboxes = document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]');
    mesCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            localStorage.setItem(checkbox.id, checkbox.checked);
            updateDropdownLabel('dropdownMes', mesCheckboxes);
        });
        // Cargar estado guardado
        checkbox.checked = localStorage.getItem(checkbox.id) === 'true';
    });

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            localStorage.setItem(checkbox.id, checkbox.checked);
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        });
        // Cargar estado guardado
        checkbox.checked = localStorage.getItem(checkbox.id) === 'true';
    });

    // Clientes
    const clienteCheckboxes = document.querySelectorAll('#dropdownCliente ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            localStorage.setItem(checkbox.id, checkbox.checked);
            updateDropdownLabel('dropdownCliente', clienteCheckboxes)
        });
        // Cargar estado guardado
        checkbox.checked = localStorage.getItem(checkbox.id) === 'true';
    });

    // Lógica para la pestaña de gráficas
    const tabGraficas = document.getElementById('graficas-tab');
    if (tabGraficas) {
        tabGraficas.addEventListener('shown.bs.tab', function () {
            setTimeout(renderMargenClienteChart, 100);
        });
    }

    // Renderizar gráfico al cargar si estamos en la pestaña de gráficas
    if (document.querySelector('#graficas-tab').classList.contains('active')) {
        setTimeout(renderMargenClienteChart, 300);
    }

    function renderMargenClienteChart() {
        // Limpiar gráfica existente
        const container = document.getElementById('grafica-margen-clientes');
        if (container) {
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
        }
        
        // Obtener datos de la tabla
        const clientes = [];
        const margenBruto = [];
        const utilidadBruta = [];
        const meta = [];
        let minMargen = 0;
        let maxMargen = 25;
        
        document.querySelectorAll('#tabla-margen-clientes tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length > 0 && !row.classList.contains('table-info')) {
                clientes.push(cells[0].innerText.trim());
                
                const margenCell = cells[6].innerText;
                const margenValue = margenCell === '-' ? 0 : parseFloat(margenCell.replace('%', ''));
                margenBruto.push(margenValue);
                
                const utilidadCell = cells[5].innerText;
                const utilidadValue = utilidadCell === '-' ? 0 : parseFloat(utilidadCell.replace('$', '').replace(',', ''));
                utilidadBruta.push(utilidadValue);
                
                meta.push(25); // Meta fija
                
                // Actualizar rango para el eje Y
                if (margenValue < minMargen) minMargen = margenValue;
                if (margenValue > maxMargen) maxMargen = margenValue;
            }
        });
        
        // Ajustar rango para incluir la meta y valores extremos
        minMargen = Math.min(minMargen, 0) - 10;
        maxMargen = Math.max(maxMargen, 25) + 10;
        
        // Crear gráfico principal de margen bruto
        const data = [
            {
                x: clientes,
                y: margenBruto,
                name: '% Margen Bruto',
                type: 'line', 
                marker: { color: 'orange' },
                line: { shape: 'spline' },
                text: margenBruto.map(v => v.toFixed(2) + '%'),
                textposition: 'top center',
                yaxis: 'y'
            },
            {
                x: clientes,
                y: meta,
                name: 'Meta (25%)',
                type: 'scatter',
                mode: 'lines',
                line: {color: 'navy', width: 2, dash: 'dash'},
                hoverinfo: 'none',
                yaxis: 'y'
            }
        ];
        
        const layout = {
            title: 'Margen por Cliente',
            yaxis: {
                title: '% Margen Bruto',
                tickformat: ',.0f',
                range: [minMargen, maxMargen]
            },
            xaxis: {
                title: 'Clientes',
                tickangle: -45,
                type: 'category',
                showgrid: false
            },
            legend: {
                orientation: 'h', // vertical
                x: 0,          // fuera del área de la gráfica, a la derecha
                y: 1.25,
                font: {
                    size: 16      // tamaño de fuente más grande
                },
                itemsizing: 'constant'
            },
            barmode: 'group',
            hovermode: 'closest',
            margin: {b: 150, l: 50, r: 50, t: 50, pad: 10}, // aumenta el margen derecho
            showlegend: true
        };
        
        const config = {
            responsive: true,
            displayModeBar: true
        };
        
        // Renderizar gráfica principal
        Plotly.newPlot('grafica-margen-clientes', data, layout, config);
    }
});