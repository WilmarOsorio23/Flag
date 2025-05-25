// Ejecutar el script solo después de que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function () {
  
    //=============================
    //LÓGICA DE CARDS Y GRÁFICOS
    //=============================

    //Función genérica para inicializar un gráfico en una card
    function crearGraficoCard({
      cardId,
      modalId,
      canvasId,
      labelsScriptId,
      valuesScriptId,
      chartVarName,
      labelText,
      bgColor,
      borderColor
    }) {
        
      // Obtener elementos DOM necesarios
      const card = document.getElementById(cardId);
      const modal = new bootstrap.Modal(document.getElementById(modalId));
      
      // Al hacer clic sobre la card, se muestra el modal con el gráfico
      card.addEventListener('click', function () {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        //Evita errores de superposición al abrir reiteradas veces
        if (window[chartVarName]) {
          window[chartVarName].destroy();
        }
        
        //Construcción del gráfico de barras
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
        
        //Mostrar el modal
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