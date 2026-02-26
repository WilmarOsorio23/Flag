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
