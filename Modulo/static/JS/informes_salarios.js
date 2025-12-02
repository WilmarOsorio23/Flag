document.addEventListener('DOMContentLoaded', function () {
    //=============================
    // LÓGICA DE CARDS Y GRÁFICOS
    //=============================
  
    const card = document.getElementById('cardLinea');
    const modalElement = document.getElementById('graficoLineaModal');
  
    if (card && modalElement) {
      const modal = new bootstrap.Modal(modalElement);
  
      card.addEventListener('click', function () {
        const canvas = document.getElementById('graficoLineaCanvas');
        if (!canvas) return;
  
        const ctx = canvas.getContext('2d');
  
        if (window.lineaChart) {
          window.lineaChart.destroy();
        }
  
        const labelsScript = document.getElementById('labels-linea');
        const valuesScript = document.getElementById('values-linea');
        if (!labelsScript || !valuesScript) return;
  
        const labels = JSON.parse(labelsScript.textContent);
        const values = JSON.parse(valuesScript.textContent);
  
        window.lineaChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Colaboradores Certificados por Línea',
              data: values,
              backgroundColor: 'rgba(13, 202, 240, 0.5)',
              borderColor: 'rgba(13, 202, 240, 1)',
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
  
    //  =============================
    //  LÓGICA DE ORDENAMIENTO DE TABLA
    //  =============================
  
    const table = document.getElementById('nominaTable');
    if (!table) {
      // Si no hay tabla (por ejemplo sin resultados), igual inicializamos reset filtros abajo.
      inicializarResetFiltros();
      return;
    }
  
    const tbody = table.querySelector('tbody');
    const sortableHeaders = table.querySelectorAll('.sortable');
  
    // Función para obtener índice de columna desde data-sort
    function getColumnIndex(sortColumn) {
      const headers = table.querySelectorAll('thead th');
      for (let i = 0; i < headers.length; i++) {
        if (headers[i].dataset.sort === sortColumn) {
          return i + 1; // nth-child es 1-based
        }
      }
      return 1;
    }
  
    // Función de ordenamiento
    function sortTable(column, direction) {
      const rows = Array.from(tbody.querySelectorAll('tr'));
  
      // Actualizar indicadores visuales en todos los encabezados
      sortableHeaders.forEach(header => {
        header.dataset.direction = header.dataset.sort === column ? direction : 'default';
      });
  
      const columnIndex = getColumnIndex(column);
  
      rows.sort((a, b) => {
        const aCell = a.querySelector(`td:nth-child(${columnIndex})`);
        const bCell = b.querySelector(`td:nth-child(${columnIndex})`);
        const aValue = (aCell ? aCell.textContent : '').trim();
        const bValue = (bCell ? bCell.textContent : '').trim();
  
        // Comparación numérica para documento y año
        if (['documento_colaborador', 'año', 'anios'].includes(column)) {
          const numA = Number(aValue.replace(/\D/g, '') || 0);
          const numB = Number(bValue.replace(/\D/g, '') || 0);
  
          if (direction === 'asc') {
            return numA - numB;
          }
          if (direction === 'desc') {
            return numB - numA;
          }
          return 0;
        }
  
        // Comparación de cadenas para otros campos
        if (direction === 'asc') {
          return aValue.localeCompare(bValue);
        }
        if (direction === 'desc') {
          return bValue.localeCompare(aValue);
        }
        return 0;
      });
  
      // Reinsertar filas ordenadas
      rows.forEach(row => tbody.appendChild(row));
  
      // Accesibilidad: actualizar etiquetas ARIA
      sortableHeaders.forEach(header => {
        const col = header.dataset.sort;
        const dir = header.dataset.direction;
  
        let dirText = '';
        if (dir === 'asc') dirText = 'ascendente';
        if (dir === 'desc') dirText = 'descendente';
  
        header.setAttribute(
          'aria-label',
          `Ordenar por ${col} ${dirText}`.trim()
        );
      });
    }
  
    // Función centralizada para disparar el ordenamiento
    function triggerSort(header) {
      const column = header.dataset.sort;
      const currentDirection = header.dataset.direction || 'default';
  
      let newDirection;
      switch (currentDirection) {
        case 'default':
          newDirection = 'asc';
          break;
        case 'asc':
          newDirection = 'desc';
          break;
        case 'desc':
          newDirection = 'default';
          break;
        default:
          newDirection = 'asc';
          break;
      }
  
      sortTable(column, newDirection);
    }
  
    // Inicializar headers ordenables
    sortableHeaders.forEach(header => {
      header.dataset.direction = 'default';
      header.setAttribute('title', 'Haga clic para ordenar');
      header.setAttribute('tabindex', '0');
  
      header.addEventListener('click', function () {
        triggerSort(this);
      });
  
      header.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          triggerSort(this);
        }
      });
    });
  
    // =============================
    // LÓGICA DE REINICIO DE FILTROS
    // =============================
  
    inicializarResetFiltros();
  
    function inicializarResetFiltros() {
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
            if (input.type !== 'hidden' && input.name !== 'csrfmiddlewaretoken') {
              input.value = '';
            }
          });
        });
      } else {
        if (!resetBtn) console.error('❌ No se encontró el botón con id="btn-reset-filtros"');
        if (!form) console.error('❌ No se encontró ningún formulario');
      }
    }
  });
  