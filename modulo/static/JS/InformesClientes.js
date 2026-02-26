document.addEventListener('DOMContentLoaded', function () {

    // =============================
    // LÓGICA DE CARDS Y GRÁFICOS
    // =============================
  
    /**
     * Función genérica para crear un gráfico en un modal al hacer clic en una card.
     * @param {Object} config - Configuración del gráfico
     */
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
  
      if (!card) return;
  
      card.addEventListener('click', function () {
        const ctx = document.getElementById(canvasId).getContext('2d');
  
        // Destruir gráfico previo si existe
        if (window[chartVarName]) {
          window[chartVarName].destroy();
        }
  
        // Crear nuevo gráfico
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
              legend: { display: type !== 'bar', position: 'bottom' }
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
  
    // === Gráficos por categoría ===
  
    crearGraficoCard({
      cardId: 'cardTipoCliente',
      modalId: 'graficoTipoClienteModal',
      canvasId: 'graficoTipoClienteCanvas',
      labelsScriptId: 'labels-tipo-cliente',
      valuesScriptId: 'values-tipo-cliente',
      chartVarName: 'tipoClienteChart',
      labelText: 'Tipo de Cliente',
      bgColor: 'rgba(255, 193, 7, 0.5)',
      borderColor: 'rgba(255, 193, 7, 1)'
    });
  
    crearGraficoCard({
      cardId: 'cardPaises',
      modalId: 'graficoPaisesModal',
      canvasId: 'graficoPaisesCanvas',
      labelsScriptId: 'labels-paises',
      valuesScriptId: 'values-paises',
      chartVarName: 'paisesChart',
      labelText: 'País',
      bgColor: 'rgba(13, 202, 240, 0.5)',
      borderColor: 'rgba(13, 202, 240, 1)'
    });
  
    crearGraficoCard({
      cardId: 'cardNacionalidad',
      modalId: 'graficoNacionalidadModal',
      canvasId: 'graficoNacionalidadCanvas',
      labelsScriptId: 'labels-nacionalidad',
      valuesScriptId: 'values-nacionalidad',
      chartVarName: 'nacionalidadChart',
      labelText: 'Nacionalidad',
      bgColor: ['rgba(108, 117, 125, 0.7)', 'rgba(33, 37, 41, 0.7)'],
      borderColor: ['rgba(108, 117, 125, 1)', 'rgba(33, 37, 41, 1)'],
      type: 'bar'
    });
  
    crearGraficoCard({
      cardId: 'cardActivosInactivos',
      modalId: 'graficoActivosInactivosModal',
      canvasId: 'graficoActivosInactivosCanvas',
      labelsScriptId: 'labels-activos',
      valuesScriptId: 'values-activos',
      chartVarName: 'activosChart',
      labelText: 'Estado',
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