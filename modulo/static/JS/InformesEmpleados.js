document.addEventListener('DOMContentLoaded', function () {

  //=============================
  // LÓGICA DE CARDS Y GRÁFICOS
  //=============================
  // Lógica para gráfico Activos/Inactivos (tipo doughnut)
  const cardAI = document.getElementById('cardActivosInactivos');
  const modalAIElement = document.getElementById('graficoActivosInactivosModal');

  if (cardAI && modalAIElement) {
    const modalAI = new bootstrap.Modal(modalAIElement);

    cardAI.addEventListener('click', function () {
      const ctx = document.getElementById('graficoActivosInactivosCanvas').getContext('2d');

      if (window.activosChart) {
        window.activosChart.destroy();
      }

      window.activosChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: JSON.parse(document.getElementById('labels-activos').textContent),
          datasets: [{
            label: 'Estado',
            data: JSON.parse(document.getElementById('values-activos').textContent),
            backgroundColor: ['rgba(25, 135, 84, 0.7)', 'rgba(220, 53, 69, 0.7)'],
            borderColor: ['rgba(25, 135, 84, 1)', 'rgba(220, 53, 69, 1)'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });

      modalAI.show();
    });
  }

  // Función genérica para gráficos de barra
  function crearGraficoCard({ cardId, modalId, canvasId, labelsScriptId, valuesScriptId, chartVarName, labelText, bgColor, borderColor }) {
    const card = document.getElementById(cardId);
    const modalElement = document.getElementById(modalId);
    if (!card || !modalElement) return;

    const modal = new bootstrap.Modal(modalElement);

    card.addEventListener('click', function () {
      const ctx = document.getElementById(canvasId).getContext('2d');

      if (window[chartVarName]) {
        window[chartVarName].destroy();
      }

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
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Cantidad' }
            }
          }
        }
      });

      modal.show();
    });
  }

  crearGraficoCard({
    cardId: 'cardCertificadosSAP',
    modalId: 'graficoCertificadosSAPModal',
    canvasId: 'graficoCertificadosSAPCanvas',
    labelsScriptId: 'labels-data',
    valuesScriptId: 'values-data',
    chartVarName: 'certificadosChart',
    labelText: 'Certificados SAP',
    bgColor: 'rgba(13, 110, 253, 0.5)',
    borderColor: 'rgba(13, 110, 253, 1)'
  });

  crearGraficoCard({
    cardId: 'cardOtrasCertificaciones',
    modalId: 'graficoOtrasCertificacionesModal',
    canvasId: 'graficoOtrasCertificacionesCanvas',
    labelsScriptId: 'labels-otras',
    valuesScriptId: 'values-otras',
    chartVarName: 'otrasCertificacionesChart',
    labelText: 'Otras Certificaciones',
    bgColor: 'rgba(255, 193, 7, 0.5)',
    borderColor: 'rgba(255, 193, 7, 1)'
  });

  crearGraficoCard({
    cardId: 'cardPostgrados',
    modalId: 'graficoPostgradosModal',
    canvasId: 'graficoPostgradosCanvas',
    labelsScriptId: 'labels-postgrados',
    valuesScriptId: 'values-postgrados',
    chartVarName: 'postgradosChart',
    labelText: 'Postgrados',
    bgColor: 'rgba(220, 53, 69, 0.5)',
    borderColor: 'rgba(220, 53, 69, 1)'
  });

  crearGraficoCard({
    cardId: 'cardPorModulo',
    modalId: 'graficoPorModuloModal',
    canvasId: 'graficoPorModuloCanvas',
    labelsScriptId: 'labels-modulo',
    valuesScriptId: 'values-modulo',
    chartVarName: 'moduloChart',
    labelText: 'Empleados por Módulo',
    bgColor: 'rgba(54, 162, 235, 0.5)',
    borderColor: 'rgba(54, 162, 235, 1)'
  });

  crearGraficoCard({
    cardId: 'cardPorPerfil',
    modalId: 'graficoPorPerfilModal',
    canvasId: 'graficoPorPerfilCanvas',
    labelsScriptId: 'labels-perfil',
    valuesScriptId: 'values-perfil',
    chartVarName: 'perfilChart',
    labelText: 'Empleados por Perfil',
    bgColor: 'rgba(255, 99, 132, 0.5)',
    borderColor: 'rgba(255, 99, 132, 1)'
  });

  crearGraficoCard({
    cardId: 'cardPorLinea',
    modalId: 'graficoPorLineaModal',
    canvasId: 'graficoPorLineaCanvas',
    labelsScriptId: 'labels-linea',
    valuesScriptId: 'values-linea',
    chartVarName: 'lineaChart',
    labelText: 'Empleados por Línea',
    bgColor: 'rgba(75, 192, 192, 0.5)',
    borderColor: 'rgba(75, 192, 192, 1)'
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