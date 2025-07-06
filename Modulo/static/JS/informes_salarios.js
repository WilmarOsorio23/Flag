document.addEventListener('DOMContentLoaded', function() {

        //=============================
        //LÓGICA DE CARDS Y GRÁFICOS
        //=============================
    
        const card = document.getElementById('cardLinea');
        const modal = new bootstrap.Modal(document.getElementById('graficoLineaModal'));
      
        card.addEventListener('click', function () {
          const ctx = document.getElementById('graficoLineaCanvas').getContext('2d');
          
          if (window.lineaChart) {
            window.lineaChart.destroy();
          }
      
          window.lineaChart = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: JSON.parse(document.getElementById('labels-linea').textContent),
              datasets: [{
                label: 'Colaboradores Certificados por Línea',
                data: JSON.parse(document.getElementById('values-linea').textContent),
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


    //  =============================
    //  LÓGICA DE ORDENAMIENTO DE TABLA
    //  =============================
    
    // Función de ordenamiento mejorada
    function sortTable(column, direction) {
        const table = document.getElementById('nominaTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        // Actualizar indicadores visuales en todos los encabezados
        document.querySelectorAll('.sortable').forEach(header => {
            // Resetear todos los encabezados a 'default'
            header.dataset.direction = header.dataset.sort === column ? direction : 'default';
        });

        rows.sort((a, b) => {
            const aValue = a.querySelector(`td:nth-child(${getColumnIndex(column)})`).textContent.trim();
            const bValue = b.querySelector(`td:nth-child(${getColumnIndex(column)})`).textContent.trim();
            
            // Comparación numérica para documentos y años
            if (['documento_colaborador', 'año'].includes(column)) {
                return direction === 'asc' 
                    ? Number(aValue || 0) - Number(bValue || 0)
                    : direction === 'desc'
                    ? Number(bValue || 0) - Number(aValue || 0)
                    : 0;
            }
            
            // Comparación de cadenas para otros campos
            return direction === 'asc'
                ? aValue.localeCompare(bValue)
                : direction === 'desc'
                ? bValue.localeCompare(aValue)
                : 0;
        });

        // Reinsert sorted rows
        rows.forEach(row => tbody.appendChild(row));

        // Mejora de accesibilidad: Actualizar etiquetas ARIA
        document.querySelectorAll('.sortable').forEach(header => {
            const column = header.dataset.sort;
            const direction = header.dataset.direction;
            
            header.setAttribute('aria-label', 
                `Ordenar por ${column} ${direction === 'asc' ? 'ascendente' : direction === 'desc' ? 'descendente' : ''}`
            );
        });
    }

    // Función para obtener índice de columna
    function getColumnIndex(sortColumn) {
        const headers = document.querySelectorAll('#nominaTable thead th');
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].dataset.sort === sortColumn) {
                return i + 1;
            }
        }
        return 1;
    }

    // Manejar clics en encabezados
    document.querySelectorAll('.sortable').forEach(header => {
        // Evento de clic
        header.addEventListener('click', function() {
            triggerSort(this);
        });

        // Soporte para teclado (Enter y Espacio)
        header.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                triggerSort(this);
            }
        });

        // Establecer dirección inicial a 'default'
        header.dataset.direction = 'default';
    });

    // Función centralizada para ordenar
    function triggerSort(header) {
        const column = header.dataset.sort;
        const currentDirection = header.dataset.direction;
        
        let newDirection;
        switch(currentDirection) {
            case 'default':
                newDirection = 'asc';
                break;
            case 'asc':
                newDirection = 'desc';
                break;
            case 'desc':
                newDirection = 'default';
                break;
        }

        sortTable(column, newDirection);
    }

    // Mejora de accesibilidad: Tooltip descriptivo
    function addTooltips() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.setAttribute('title', 'Haga clic para ordenar');
            header.setAttribute('tabindex', '0'); // Hacerlo enfocable con teclado
        });
    }

    // Inicializar tooltips
    addTooltips();

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