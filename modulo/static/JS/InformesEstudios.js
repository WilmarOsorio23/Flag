document.addEventListener('DOMContentLoaded', function() {

  //=============================
  //LÓGICA DE CARDS Y GRÁFICOS
  //=============================
  // Línea
  const cardLinea = document.getElementById('cardLinea');
  const modalLinea = new bootstrap.Modal(document.getElementById('graficoLineaModal'));

  cardLinea.addEventListener('click', function () {
    const ctx = document.getElementById('graficoLineaCanvas').getContext('2d');
    if (window.lineaChart) window.lineaChart.destroy();

    window.lineaChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: JSON.parse(document.getElementById('labels-linea').textContent),
        datasets: [{
          label: 'Estudios por Línea',
          data: JSON.parse(document.getElementById('values-linea').textContent),
          backgroundColor: 'rgba(13, 202, 240, 0.5)',
          borderColor: 'rgba(13, 202, 240, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Cantidad' }
          }
        }
      }
    });

    modalLinea.show();
  });

  // Institución
  const cardInstitucion = document.getElementById('cardInstitucion');
  const modalInstitucion = new bootstrap.Modal(document.getElementById('graficoInstitucionModal'));

  cardInstitucion.addEventListener('click', function () {
    const ctx = document.getElementById('graficoInstitucionCanvas').getContext('2d');
    if (window.institucionChart) window.institucionChart.destroy();

    window.institucionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: JSON.parse(document.getElementById('labels-institucion').textContent),
        datasets: [{
          label: 'Estudios por Institución',
          data: JSON.parse(document.getElementById('values-institucion').textContent),
          backgroundColor: 'rgba(25, 135, 84, 0.5)',
          borderColor: 'rgba(25, 135, 84, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Cantidad' }
          }
        }
      }
    });

    modalInstitucion.show();
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
