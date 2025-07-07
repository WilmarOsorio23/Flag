document.addEventListener('DOMContentLoaded', function() {
    // Cargar jQuery si no está presente
    if (!window.jQuery) {
        const script = document.createElement('script');
        script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
        document.head.appendChild(script);
    }

    // Elementos que NO dependen de jQuery
    const MESES_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

    // Inicializar tabs
    const triggerTabList = [].slice.call(document.querySelectorAll('#myTab button'))
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl)
        triggerEl.addEventListener('click', event => {
            event.preventDefault()
            tabTrigger.show()
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
    mesCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownMes', mesCheckboxes)
        )
    );

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        )
    );

    // Clientes
    const clienteCheckboxes = document.querySelectorAll('#dropdownCliente ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownCliente', clienteCheckboxes)
        )
    );

    // Verificar carga de jQuery
    const checkJquery = setInterval(() => {
        if (window.jQuery) {
            clearInterval(checkJquery);
            inicializarEventos();
        }
    }, 100);


    // Función para inicializar todo lo que depende de jQuery
    function inicializarEventos() {
        // Custom jQuery selector
        jQuery.expr[':'].contains = function(a, i, m) {
            return jQuery(a).text().toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
        };

        // Elementos que SÍ dependen de jQuery
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const diciembreInputs = document.querySelectorAll('input[name^="diciembre_"]');
        if (diciembreInputs.length > 0) {
            let timeout;
            diciembreInputs.forEach(input => {
                input.addEventListener('input', function() {
                    clearTimeout(timeout);
                    timeout = setTimeout(recalcularIndicadores, 500);
                });
            });
        } else {
            console.log('No se encontraron inputs de diciembre');
        }

        function recalcularIndicadores() {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'recalculando';
            loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Recalculando...</span></div>';
            document.body.appendChild(loadingIndicator);
        
            // Obtener los valores actuales del formulario de filtros
            const formData = new FormData(document.querySelector('form[method="GET"]'));
            const filters = {
                Anio: formData.get('Anio'),
                Mes: Array.from(document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]:checked')).map(cb => cb.value),
                LineaId: Array.from(document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]:checked')).map(cb => cb.value),
                ClienteId: Array.from(document.querySelectorAll('#dropdownCliente ~ .dropdown-menu input[type="checkbox"]:checked')).map(cb => cb.value)
            };
        
            const diciembreData = {};
            document.querySelectorAll('input[name^="diciembre_"]').forEach(input => {
                const partes = input.name.split('_');
                const clienteId = partes[partes.length - 1];
                const tipo = partes.slice(1, partes.length - 1).join('_');
                
                if (!diciembreData[clienteId]) {
                    diciembreData[clienteId] = {
                        trabajado: '0',
                        facturado: '0',
                        costo: '0',
                        valor_facturado: '0'
                    };
                }
                diciembreData[clienteId][tipo] = input.value || '0';
            });
                
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'recalculate',
                    filters: filters,
                    diciembre: diciembreData
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new TypeError("La respuesta no es JSON");
                }
                return response.json();
            })
            .then(data => {
                actualizarTabla(data);
                document.body.removeChild(loadingIndicator);
            })
            .catch(error => {
                console.error('Error en fetch:', error);
                document.body.removeChild(loadingIndicator);
                
                let errorMsg = 'Error al recalcular indicadores';
                if (error.message.includes('Unexpected token')) {
                    errorMsg = 'El servidor devolvió una respuesta no válida';
                } else if (error.message.includes('400')) {
                    errorMsg = 'Datos enviados incorrectos';
                }
                
                alert(errorMsg);
                console.error('Detalles del error:', error);
            });
        }

        function actualizarTabla(data) {
            const actualizarFila = (mesNum, datosMes) => {
                const mesNombre = MESES_ES[parseInt(mesNum) - 1];
                const $fila = $(`#totales tbody tr:not(.diciembre-anterior):has(td:first-child:contains("${mesNombre}"))`);
                
                if ($fila.length) {
                    const $celdas = $fila.find('td');
                    
                    // Actualizar datos base
                    $celdas.eq(1).text(datosMes.Dias);
                    $celdas.eq(2).text(parseFloat(datosMes.Horas).toFixed(2));
                    
                    let indice = 3;
                    Clientes.forEach(cliente => {
                        const clienteKey = cliente.Nombre_Cliente;
                        if (datosMes.Clientes[clienteKey]) {
                            const clienteData = datosMes.Clientes[clienteKey];
                            
                            $celdas.eq(indice++).text(parseFloat(clienteData.Trabajado).toFixed(2));
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Costo).toFixed(2));
                            $celdas.eq(indice++).text(parseFloat(clienteData.Facturado.horas).toFixed(2));
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Facturado.valor).toFixed(2));
                            $celdas.eq(indice++).text(parseFloat(clienteData.Pendiente.horas).toFixed(2));
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Pendiente.valor).toFixed(2));
                        } else {
                            indice += 6;
                        }
                    });
                }
            };
        
            // Actualizar filas por mes
            if (data.general) {
                Object.entries(data.general).forEach(([mesNum, datosMes]) => {
                    actualizarFila(mesNum, datosMes);
                });
            }
        
            // Recalcular totales
                Clientes.forEach(cliente => {
                    const clienteKey = cliente.Nombre_Cliente;
                let totales = {
                    trabajado: 0,
                    costo: 0,
                    facturado_horas: 0,
                    facturado_valor: 0
                };

                // Sumar valores de diciembre si existe
                const $diciembreInputs = $(`.diciembre-anterior input[name^="diciembre_"][name$="${cliente.ClienteId}"]`);
                if ($diciembreInputs.length) {
                    totales.trabajado += parseFloat($diciembreInputs.filter('[name^="diciembre_trabajado_"]').val() || 0);
                    totales.costo += parseFloat($diciembreInputs.filter('[name^="diciembre_costo_"]').val() || 0);
                    totales.facturado_horas += parseFloat($diciembreInputs.filter('[name^="diciembre_facturado_"]').val() || 0);
                    totales.facturado_valor += parseFloat($diciembreInputs.filter('[name^="diciembre_valor_facturado_"]').val() || 0);
                }

                // Sumar valores de cada mes
                $(`#totales tbody tr:not(.diciembre-anterior) td[data-cliente="${clienteKey}"]`).each(function() {
                    const $td = $(this);
                    const valor = parseFloat($td.text().replace('$', '').replace(',', '') || 0);
                    const index = $td.index();
                    
                    // Determinar qué tipo de valor es basado en su posición
                    const posicionRelativa = (index - 3) % 6; // 3 es el offset por las columnas fijas
                    switch(posicionRelativa) {
                        case 0: totales.trabajado += valor; break;
                        case 1: totales.costo += valor; break;
                        case 2: totales.facturado_horas += valor; break;
                        case 3: totales.facturado_valor += valor; break;
                    }
                });

                // Actualizar los totales calculados
                $(`.total-trabajado[data-cliente="${clienteKey}"]`).text(totales.trabajado.toFixed(2));
                $(`.total-costo[data-cliente="${clienteKey}"]`).text('$' + totales.costo.toFixed(2));
                $(`.total-facturado-horas[data-cliente="${clienteKey}"]`).text(totales.facturado_horas.toFixed(2));
                $(`.total-facturado-valor[data-cliente="${clienteKey}"]`).text('$' + totales.facturado_valor.toFixed(2));

                // Usar los valores de pendientes del backend
                if (data.totales && data.totales[clienteKey]) {
                    $(`.total-pendiente-horas[data-cliente="${clienteKey}"]`).text(
                        parseFloat(data.totales[clienteKey].Pendiente_horas || 0).toFixed(2)
                    );
                    $(`.total-pendiente-valor[data-cliente="${clienteKey}"]`).text(
                        '$' + parseFloat(data.totales[clienteKey].Pendiente_valor || 0).toFixed(2)
                    );

                    // Actualizar diferencias y margen usando los valores del backend para pendientes
                    const pendienteHoras = parseFloat(data.totales[clienteKey].Pendiente_horas || 0);
                    const pendienteValor = parseFloat(data.totales[clienteKey].Pendiente_valor || 0);
                    
                    const difHoras = totales.trabajado - totales.facturado_horas - pendienteHoras;
                    const difValor = (totales.facturado_valor + pendienteValor) - totales.costo;
                    const margenBruto = totales.facturado_valor + pendienteValor !== 0 
                        ? ((totales.facturado_valor + pendienteValor - totales.costo) / 
                           (totales.facturado_valor + pendienteValor) * 100)
                        : 0;

                    $(`tr:contains("Dif fact / Tbjo") th[data-cliente="${clienteKey}"]`)
                        .text(difHoras.toFixed(2))
                        .next('th')
                        .text('$' + difValor.toFixed(2));

                    $(`tr:contains("% Margen Bruto") th[data-cliente="${clienteKey}"]`)
                        .text(margenBruto.toFixed(2) + '%');
                }
            });

            // Calcular totales de días y horas
            let totalDias = 0;
            let totalHoras = 0;
            $('#totales tbody tr:not(.diciembre-anterior)').each(function() {
                totalDias += parseFloat($(this).find('td:eq(1)').text() || 0);
                totalHoras += parseFloat($(this).find('td:eq(2)').text() || 0);
            });
            
            const numMeses = $('#totales tbody tr:not(.diciembre-anterior)').length || 1;
            $('.total-dias').text((totalDias / numMeses).toFixed(2));
            $('.total-horas').text((totalHoras / numMeses).toFixed(2));
        }
    }
});

// Variable global MESES para uso en las funciones
const MESES = {
    '1': 'Enero', '2': 'Febrero', '3': 'Marzo', '4': 'Abril',
    '5': 'Mayo', '6': 'Junio', '7': 'Julio', '8': 'Agosto',
    '9': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
};

// Estilos para el indicador de carga
const style = document.createElement('style');
style.textContent = `
    .recalculando {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .recalculando .spinner-border {
        width: 3rem;
        height: 3rem;
    }
`;
document.head.appendChild(style);

// --- GRAFICAS ---
// Renderizar cada gráfica solo cuando se activa su pestaña
let graficaTotalesRenderizada = false;
let graficaLineasRenderizada = false;

document.getElementById('grafico-totales-tab').addEventListener('shown.bs.tab', function () {
    if (!graficaTotalesRenderizada) {
        renderizarGraficaTotales();
        graficaTotalesRenderizada = true;
    }
});
document.getElementById('grafico-lineas-tab').addEventListener('shown.bs.tab', function () {
    if (!graficaLineasRenderizada) {
        renderizarGraficaLineas();
        graficaLineasRenderizada = true;
    }
});

// Paleta de colores pastel para las métricas
function pastelColor(idx, total) {
    const hue = (idx * 360 / total) % 360;
    return `hsl(${hue}, 70%, 70%)`;
}

function renderizarGraficaTotales() {
    // Obtener datos de la tabla de totales generales
    const meses = [];
    const clientes = Clientes.map(c => c.Nombre_Cliente);
    const metricas = [
        { key: 'Trabajado', label: 'Trabajado', color: '#1976d2' },
        { key: 'FacturadoHoras', label: 'Facturado', color: '#fbc02d' },
        { key: 'PendienteHoras', label: 'Pend.Fact', color: '#7b1fa2' }
    ];
    // cliente -> métrica -> array de valores por mes
    const datosPorCliente = {};
    clientes.forEach(cliente => {
        datosPorCliente[cliente] = {};
        metricas.forEach(m => datosPorCliente[cliente][m.key] = []);
    });
    const tabla = document.querySelector('#totales table');
    if (tabla) {
        const filas = tabla.querySelectorAll('tbody tr:not(.diciembre-anterior)');
        filas.forEach(fila => {
            const celdas = fila.querySelectorAll('td');
            if (celdas.length > 0) {
                meses.push(celdas[0].textContent.trim());
                let idx = 3;
                clientes.forEach(cliente => {
                    datosPorCliente[cliente]['Trabajado'].push(parseFloat(celdas[idx]?.textContent.replace(',', '') || '0'));
                    // Saltar $ Costo (idx+1)
                    datosPorCliente[cliente]['FacturadoHoras'].push(parseFloat(celdas[idx+2]?.textContent.replace(',', '') || '0'));
                    // Saltar $ Facturado (idx+3)
                    datosPorCliente[cliente]['PendienteHoras'].push(parseFloat(celdas[idx+4]?.textContent.replace(',', '') || '0'));
                    // Saltar $ Pend.Fact (idx+5)
                    idx += 6;
                });
            }
        });
    }
    // Para cada mes, para cada cliente, para cada métrica, crear una barra
    const labels = [];
    meses.forEach(mes => {
        clientes.forEach(cliente => {
            labels.push(`${cliente} - ${mes}`);
        });
    });
    // Para cada ítem, un dataset, con los valores de todos los clientes y meses
    const datasets = metricas.map((metrica, midx) => {
        const data = [];
        meses.forEach((mes, mesIdx) => {
            clientes.forEach(cliente => {
                data.push(datosPorCliente[cliente][metrica.key][mesIdx] || 0);
            });
        });
        return {
            label: metrica.label,
            data: data,
            backgroundColor: pastelColor(midx, metricas.length),
            borderColor: pastelColor(midx, metricas.length),
            borderWidth: 1
        };
    });
    const ctx1 = document.getElementById('grafico-totales-generales').getContext('2d');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Indicadores por Cliente y Mes' }
            },
            scales: {
                x: {
                    stacked: false,
                    barPercentage: 0.85,
                    categoryPercentage: 0.6
                },
                y: { beginAtZero: true }
            }
        }
    });
}

function renderizarGraficaLineas() {
    if (window.Lineas && window.ResultadosLineas) {
        const lineas = window.Lineas;
        const resultados = window.ResultadosLineas;
        
        const metricas = [
            { key: 'Trabajado', label: 'Trabajado', color: '#1976d2' },
            { key: 'FacturadoHoras', label: 'Facturado', color: '#fbc02d' },
            { key: 'PendienteHoras', label: 'Pend.Fact', color: '#7b1fa2' }
        ];
        // Obtener los meses de la primera línea (ordenados)
        const mesesLinea = Object.keys(resultados[lineas[0].LineaId]?.general || {}).sort((a, b) => parseInt(a) - parseInt(b));
        
        // labels: para cada mes, para cada línea, el label será "Línea - Mes"
        const labels = [];
        mesesLinea.forEach(mes => {
            lineas.forEach(linea => {
                labels.push(`${linea.Linea} - ${MESES[mes] || mes}`);
            });
        });
        
        // Para cada ítem, un dataset, con los valores de todas las líneas y meses
        const datasets = metricas.map((metrica, midx) => {
            const data = [];
            mesesLinea.forEach((mes, mesIdx) => {
                lineas.forEach(linea => {
                    let valor = 0;
                    if (metrica.key === 'Trabajado')
                        valor = parseFloat(resultados[linea.LineaId]?.general[mes]?.Trabajado || 0);
                    else if (metrica.key === 'FacturadoHoras')
                        valor = parseFloat(resultados[linea.LineaId]?.general[mes]?.Facturado?.horas || 0);
                    else if (metrica.key === 'PendienteHoras')
                        valor = parseFloat(resultados[linea.LineaId]?.general[mes]?.Pendiente?.horas || 0);
                    
                    data.push(valor);
                });
            });
            return {
                label: metrica.label,
                data: data,
                backgroundColor: pastelColor(midx, metricas.length),
                borderColor: pastelColor(midx, metricas.length),
                borderWidth: 1
            };
        });
        
        const ctx2 = document.getElementById('grafico-totales-linea').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Indicadores por Línea y Mes' }
                },
                scales: {
                    x: {
                        stacked: false,
                        barPercentage: 0.85,
                        categoryPercentage: 0.6
                    },
                    y: { beginAtZero: true }
                }
            }
        });
    }
}