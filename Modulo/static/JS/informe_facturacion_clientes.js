document.addEventListener('DOMContentLoaded', function () {
    const graficosData = JSON.parse(document.getElementById('graficos-data').textContent || '[]');

    // Actualiza el texto del dropdown al seleccionar/desmarcar opciones
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.nextSibling.textContent.trim());

        if (selectedOptions.length === 0) {
            button.textContent = selectedText;
        } else if (selectedOptions.length === 1) {
        button.textContent = selectedOptions[0];
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`;
        }
    }


    // Meses
    const clienteCheckboxes = document.querySelectorAll('#dropdownMes ~ .dropdown-menu input[type="checkbox"]');
    clienteCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownMes', clienteCheckboxes)
        )
    );

    // Líneas
    const lineaCheckboxes = document.querySelectorAll('#dropdownLinea ~ .dropdown-menu input[type="checkbox"]');
    lineaCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownLinea', lineaCheckboxes)
        )
    );

    // ceco
    const ConsultorCheckboxes = document.querySelectorAll('#dropdownCeco ~ .dropdown-menu input[type="checkbox"]');
    ConsultorCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownCeco', ConsultorCheckboxes)
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
    const formatValue = (value) => {
        if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';  // Billones
        if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';  // Millones
        return value.toFixed(1);  // Valor sin formato especial
    };

     graficosData.forEach(grafico => {
        const ctx = document.getElementById(`grafico-${grafico.tipo}`);
        if (!ctx) return;

        if (grafico.tipo === 'modulos') {
            new Chart(ctx, {
                type: 'bar',
                plugins: [ChartDataLabels],
                data: {
                    labels: grafico.config.labels,
                    datasets: [{
                        ...grafico.config.datasets[0],
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: formatValue,
                            color: '#333',
                            font: { weight: 'bold' }
                        }
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            top: 30,
                            bottom: 80, // Más espacio para la leyenda abajo
                            left: 20,
                            right: 20
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            align: 'start',
                            labels: {
                                generateLabels: function(chart) {
                                    if (grafico.config.descripciones_colores) {
                                        return Object.entries(grafico.config.descripciones_colores).map(([descripcion, color]) => ({
                                            text: descripcion,
                                            fillStyle: color,
                                            strokeStyle: color.replace('0.7', '1'),
                                            lineWidth: 1,
                                            hidden: false,
                                            font: {
                                                size: 12
                                            }
                                        }));
                                    }
                                    return Chart.defaults.plugins.legend.labels.generateLabels(chart);
                                },
                                boxWidth: 20,
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'rect',
                                textAlign: 'left'
                            }
                        },
                        tooltip:{
                            callbacks: {
                                afterLabel: function(context) {
                                    // Obtener la descripción correspondiente al módulo
                                    const moduloIndex = context.dataIndex;
                                    const descripcion = Object.keys(grafico.config.descripciones_colores).find(desc => 
                                        grafico.config.descripciones_colores[desc] === context.dataset.backgroundColor[moduloIndex]
                                    );
                                    return `${descripcion || 'No disponible'}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            type: 'logarithmic',
                            beginAtZero: false,
                            min: 1e6,
                            bounds: 'ticks',
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
                                    if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
                                    return value;
                                },
                                padding: 15
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45,
                                autoSkip: false
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        } else {
            // Gráfico normal para otros tipos (ej: totales por CeCo)
            new Chart(ctx, {
                type: 'bar',
                plugins: [ChartDataLabels],
                data: {
                    labels: grafico.config.labels,
                    datasets: [{
                        ...grafico.config.datasets[0],
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: formatValue,
                            color: '#333',
                            font: { weight: 'bold' }
                        }
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            top: 30
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: true }
                    },
                    scales: {
                        y: {
                            type: 'logarithmic',
                            beginAtZero: false,
                            min: 1e6,
                            bounds: 'ticks',
                            ticks: {
                                callback: function(value) {
                                    if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
                                    if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
                                    return value;
                                },
                                padding: 15
                            }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    });
});
