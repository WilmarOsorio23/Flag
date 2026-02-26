document.addEventListener('DOMContentLoaded', function () {

  /**
   * Función genérica para crear un gráfico de barras en un modal al hacer clic en una card.
   * 
   * @param {Object} params - Parámetros para configurar el gráfico.
   * @param {string} params.cardId - ID de la card que activa el modal.
   * @param {string} params.modalId - ID del modal que contiene el canvas del gráfico.
   * @param {string} params.canvasId - ID del canvas donde se renderiza el gráfico.
   * @param {string} params.labelsScriptId - ID del script con los labels del gráfico (convertido desde json_script en Django).
   * @param {string} params.valuesScriptId - ID del script con los datos del gráfico.
   * @param {string} params.chartVarName - Nombre global de la variable del gráfico (para poder destruirlo si ya existe).
   * @param {string} params.labelText - Texto que aparece como título de dataset.
   * @param {string} params.bgColor - Color de fondo de las barras.
   * @param {string} params.borderColor - Color del borde de las barras.
   */

  //=============================
  //LÓGICA DE CARDS Y GRÁFICOS
  //=============================

  function crearGraficoCard({cardId, modalId, canvasId, labelsScriptId, valuesScriptId, chartVarName, labelText, bgColor, borderColor}) {

    // Referencia a la card y al modal Bootstrap
    const card = document.getElementById(cardId);
    const modal = new bootstrap.Modal(document.getElementById(modalId));

    // Agregar evento de clic a la card
    card.addEventListener('click', function () {

       // Obtener contexto del canvas para Chart.js
      const ctx = document.getElementById(canvasId).getContext('2d');

      // Si ya existe un gráfico con ese nombre, destruirlo para evitar superposición
      if (window[chartVarName]) {
        window[chartVarName].destroy();
      }

      // Crear nuevo gráfico tipo barra
      window[chartVarName] = new Chart(ctx, {
        type: 'bar',
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
            legend: { display: false }// Oculta leyenda si solo hay un dataset
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Cantidad' }// Título del eje Y
            }
          }
        }
      });

      // Mostrar el modal con el gráfico generado
      modal.show();
    });
  }

  crearGraficoCard({
    cardId: 'cardCertificacion',          
    modalId: 'graficoCertificacionModal',    
    canvasId: 'graficoCertificacionCanvas',  
    labelsScriptId: 'labels-certificacion',  
    valuesScriptId: 'values-certificacion',  
    chartVarName: 'certificacionChart',
    labelText: 'Cantidad por Certificación',
    bgColor: 'rgba(25, 135, 84, 0.5)',
    borderColor: 'rgba(25, 135, 84, 1)'
});

  crearGraficoCard({
    cardId: 'cardLinea',
    modalId: 'graficoLineaModal',
    canvasId: 'graficoLineaCanvas',
    labelsScriptId: 'labels-linea',
    valuesScriptId: 'values-linea',
    chartVarName: 'lineaChart',
    labelText: 'Certificaciones por Línea',
    bgColor: 'rgba(13, 202, 240, 0.5)',
    borderColor: 'rgba(13, 202, 240, 1)'
  });

  // =============================
  // LÓGICA DE REINICIO DE FILTROS
  // =============================
  const resetBtn = document.getElementById('btn-reset-filtros');
  const form = document.querySelector('form');
  if (resetBtn && form) {
    resetBtn.addEventListener('click', function () {
      // Limpiar selects a su opción default (value="")
      const selects = form.querySelectorAll('select');
      selects.forEach(select => {
        select.value = '';
      });

      // Limpiar inputs de texto
      const inputs = form.querySelectorAll('input');
      inputs.forEach(input => {
        input.value = '';
      });
    });
  }

});