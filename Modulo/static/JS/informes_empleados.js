document.addEventListener('DOMContentLoaded', function () {

  //=============================
  // LÓGICA DE CARDS Y GRÁFICOS
  //=============================

  // Lógica para gráfico Activos/Inactivos (tipo doughnut)
  const cardAI = document.getElementById('cardActivosInactivos');
  const modalAI = new bootstrap.Modal(document.getElementById('graficoActivosInactivosModal'));

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

  // Función genérica para gráficos de barra
  function crearGraficoCard({ cardId, modalId, canvasId, labelsScriptId, valuesScriptId, chartVarName, labelText, bgColor, borderColor }) {
    const card = document.getElementById(cardId);
    const modal = new bootstrap.Modal(document.getElementById(modalId));

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

  //==============================
  // LÓGICA DE ORDENAMIENTO TABLA
  //==============================

  const table = document.getElementById('nominaTable');
  const headers = table.querySelectorAll('th.sortable');

  headers.forEach(header => {
    header.addEventListener('click', () => {
      const column = header.getAttribute('data-sort');
      const direction = header.getAttribute('data-direction') || 'asc';
      const newDirection = direction === 'asc' ? 'desc' : 'asc';

      sortTableByColumn(table, column, newDirection);

      headers.forEach(h => h.setAttribute('data-direction', 'default'));
      header.setAttribute('data-direction', newDirection);
    });
  });

  function sortTableByColumn(table, columnName, direction) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const columnIndex = Array.from(table.querySelectorAll('thead th'))
      .findIndex(th => th.getAttribute('data-sort') === columnName);

    rows.sort((a, b) => {
      const cellA = a.cells[columnIndex].innerText.trim();
      const cellB = b.cells[columnIndex].innerText.trim();

      if (!isNaN(cellA) && !isNaN(cellB)) {
        return direction === 'asc' ? cellA - cellB : cellB - cellA;
      }

      return direction === 'asc'
        ? cellA.localeCompare(cellB)
        : cellB.localeCompare(cellA);
    });

    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
  }
});
