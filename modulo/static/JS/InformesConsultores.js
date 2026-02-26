document.addEventListener('DOMContentLoaded', function () {

  //=============================
  // LÓGICA DE CARDS Y GRÁFICOS
  //=============================
  function crearGraficoCard({
    cardId,
    modalId,
    canvasId,
    labelsScriptId,
    valuesScriptId,
    chartVarName,
    labelText,
    bgColor,
    borderColor,
    type = 'bar'
  }) {
    const card = document.getElementById(cardId);
    const modal = new bootstrap.Modal(document.getElementById(modalId));

    card.addEventListener('click', function () {
      const ctx = document.getElementById(canvasId).getContext('2d');

      if (window[chartVarName]) {
        window[chartVarName].destroy();
      }

      window[chartVarName] = new Chart(ctx, {
        type: type,
        data: {
          labels: JSON.parse(document.getElementById(labelsScriptId).textContent),
          datasets: [{
            label: labelText,
            data: JSON.parse(document.getElementById(valuesScriptId).textContent),
            backgroundColor: bgColor,
            borderColor: borderColor,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: type === 'doughnut' }
          },
          scales: type === 'bar' ? {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Cantidad' }
            }
          } : {}
        }
      });

      modal.show();
    });
  }

  // Gráfico por Módulo
  crearGraficoCard({
    cardId: 'cardModulo',
    modalId: 'graficoModuloModal',
    canvasId: 'graficoModuloCanvas',
    labelsScriptId: 'labels-modulo',
    valuesScriptId: 'values-modulo',
    chartVarName: 'moduloChart',
    labelText: 'Consultores por Módulo',
    bgColor: 'rgba(255, 193, 7, 0.5)',
    borderColor: 'rgba(255, 193, 7, 1)',
    type: 'bar'
  });

  // Gráfico por Línea
  crearGraficoCard({
    cardId: 'cardLinea',
    modalId: 'graficoLineaModal',
    canvasId: 'graficoLineaCanvas',
    labelsScriptId: 'labels-linea',
    valuesScriptId: 'values-linea',
    chartVarName: 'lineaChart',
    labelText: 'Consultores por Línea',
    bgColor: 'rgba(13, 202, 240, 0.5)',
    borderColor: 'rgba(13, 202, 240, 1)',
    type: 'bar'
  });

  // Gráfico por Estado (Doughnut)
  crearGraficoCard({
    cardId: 'cardEstado',
    modalId: 'graficoEstadoModal',
    canvasId: 'graficoEstadoCanvas',
    labelsScriptId: 'labels-estado',
    valuesScriptId: 'values-estado',
    chartVarName: 'estadoChart',
    labelText: 'Consultores por Estado',
    bgColor: ['rgba(25, 135, 84, 0.7)', 'rgba(220, 53, 69, 0.7)'],
    borderColor: ['rgba(25, 135, 84, 1)', 'rgba(220, 53, 69, 1)'],
    type: 'doughnut'
  });

  // =============================
  // LÓGICA DE REINICIO DE FILTROS
    // =============================
    const resetBtn = document.getElementById('btn-reset-filtros');
    const form = document.querySelector('form');

    if (resetBtn && form) {

        resetBtn.addEventListener('click', function () {

        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            select.value = '';
        });

        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.value = '';
        });
        });
    } else {
        if (!resetBtn) console.error('❌ No se encontró el botón con id="btn-reset-filtros"');
        if (!form) console.error('❌ No se encontró ningún formulario');
    }
});