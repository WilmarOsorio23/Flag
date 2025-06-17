document.addEventListener('DOMContentLoaded', function () {


    //=============================
    //LÓGICA DE CARDS Y GRÁFICOS
    //=============================

    function crearGraficoCard({cardId, modalId, canvasId, labelsScriptId, valuesScriptId, chartVarName, labelText, bgColor, borderColor}) {
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
      cardId: 'cardModulo',
      modalId: 'graficoModuloModal',
      canvasId: 'graficoModuloCanvas',
      labelsScriptId: 'labels-modulo',
      valuesScriptId: 'values-modulo',
      chartVarName: 'moduloChart',
      labelText: 'Certificaciones por Módulo',
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


  //  =============================
  //  LÓGICA DE ORDENAMIENTO DE TABLA
  //  =============================
  const table = document.getElementById('nominaTable');
  const headers = table.querySelectorAll('th.sortable');

  headers.forEach(header => {
    header.addEventListener('click', () => {
      const column = header.getAttribute('data-sort');
      const direction = header.getAttribute('data-direction') || 'asc';
      const newDirection = direction === 'asc' ? 'desc' : 'asc';

      sortTableByColumn(table, column, newDirection);

      // Actualizar visualización de dirección
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