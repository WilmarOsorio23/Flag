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
                
                // Buscar fila por nombre de mes
                const $fila = $(`#totales tbody tr:not(.diciembre-anterior):has(td:first-child:contains("${mesNombre}"))`);
                
                if ($fila.length) {
                    const $celdas = $fila.find('td');
                    
                    // Actualizar datos base
                    $celdas.eq(1).text(datosMes.Dias);
                    $celdas.eq(2).text(parseFloat(datosMes.Horas).toFixed(2));
                    
                    // Índice inicial para datos de clientes (después de las 3 primeras columnas)
                    let indice = 3;
                    
                    // Iterar por cada cliente usando la variable global
                    Clientes.forEach(cliente => {
                        const clienteKey = cliente.Nombre_Cliente;
                        if (datosMes.Clientes[clienteKey]) {
                            const clienteData = datosMes.Clientes[clienteKey];
                            
                            // Trabajado
                            $celdas.eq(indice++).text(parseFloat(clienteData.Trabajado).toFixed(2));
                            // Costo
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Costo).toFixed(2));
                            // Facturado horas
                            $celdas.eq(indice++).text(parseFloat(clienteData.Facturado.horas).toFixed(2));
                            // Facturado valor
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Facturado.valor).toFixed(2));
                            // Pendiente horas
                            $celdas.eq(indice++).text(parseFloat(clienteData.Pendiente.horas).toFixed(2));
                            // Pendiente valor
                            $celdas.eq(indice++).text('$' + parseFloat(clienteData.Pendiente.valor).toFixed(2));
                        } else {
                            indice += 6; // Saltar 6 columnas si no hay datos
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
        
            // Actualizar totales
            if (data.totales) {
                const $filaTotales = $('#totales tfoot tr:first');
                let indice = 3;
                
                Clientes.forEach(cliente => {
                    const clienteKey = cliente.Nombre_Cliente;
                    if (data.totales[clienteKey]) {
                        const totales = data.totales[clienteKey];
                        
                        $filaTotales.find(`td:eq(${indice})`).text(parseFloat(totales.Trabajado).toFixed(2));
                        indice++;
                        $filaTotales.find(`td:eq(${indice})`).text('$' + parseFloat(totales.Costo).toFixed(2));
                        indice++;
                        $filaTotales.find(`td:eq(${indice})`).text(parseFloat(totales.Facturado_horas).toFixed(2));
                        indice++;
                        $filaTotales.find(`td:eq(${indice})`).text('$' + parseFloat(totales.Facturado_valor).toFixed(2));
                        indice++;
                        $filaTotales.find(`td:eq(${indice})`).text(parseFloat(totales.Pendiente_horas).toFixed(2));
                        indice++;
                        $filaTotales.find(`td:eq(${indice})`).text('$' + parseFloat(totales.Pendiente_valor).toFixed(2));
                        indice++;
                    } else {
                        indice += 6;
                    }
                });
            }
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