document.addEventListener('DOMContentLoaded', function () {
    
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
    const clienteCheckboxes = document.querySelectorAll('#dropdownCliente ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownCliente', clienteCheckboxes)
        )
    );

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        )
    );

    function selectAnio(value, label) {
        const button = document.getElementById("dropdownAnio");
        const hiddenInput = document.getElementById("selectedAnio");

        // Actualizar el texto del botón y el valor oculto
        button.textContent = label;
        hiddenInput.value = value;
    }

    // Agregar eventos a cada opción de año
    document.querySelectorAll('.anio-option').forEach(item => {
        item.addEventListener('click', function (event) {
            event.preventDefault(); // Evita que el enlace recargue la página
            selectAnio(this.getAttribute("data-value"), this.textContent);
        });
    });

    console.log("Dropdowns inicializados correctamente.");

    const graficosDataElement = document.getElementById('graficos-data');
    if (graficosDataElement) {
        const graficosPorLinea = JSON.parse(graficosDataElement.textContent);
        console.log("Datos de gráficos recibidos:", graficosPorLinea);

        graficosPorLinea.forEach((grafico, index) => {
            const canvasId = `grafico-${index + 1}`;
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.log(`Canvas con ID ${canvasId} no encontrado.`);
                return;
            }

            console.log(`Creando gráfica para: ${grafico.nombre}`);
            console.log("Labels:", grafico.labels);
            console.log("Data:", grafico.datasets[0].data);

            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: grafico.datasets[0].type, // Tipo dinámico según el gráfico
                data: {
                    labels: grafico.labels,
                    datasets: grafico.datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Meses'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: grafico.nombre === 'Total General' ? 'Totales Generales' : 'Porcentaje (%)'
                            },
                            ticks: {
                                callback: function (value) {
                                    return grafico.nombre === 'Total General' ? value.toLocaleString() : `${value}%`;
                                }
                            },
                            max: grafico.nombre === 'Total General' ? undefined : 100 // Máximo dinámico para porcentajes
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });

            console.log(`Gráfica creada para: ${grafico.nombre}`);
        });
    } else {
        console.log("Elemento graficos-data no encontrado.");
    }
    


});