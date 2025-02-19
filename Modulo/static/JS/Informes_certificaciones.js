document.addEventListener('DOMContentLoaded', function() {
    // Función de ordenamiento mejorada
    function sortTable(column, direction) {
        const table = document.getElementById('employeeReportTable');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        // Actualizar indicadores visuales en todos los encabezados
        document.querySelectorAll('.sortable').forEach(header => {
            header.dataset.direction = header.dataset.sort === column ? direction : 'default';
        });

        rows.sort((a, b) => {
            const aValue = a.querySelector(`td:nth-child(${getColumnIndex(column)})`).textContent.trim();
            const bValue = b.querySelector(`td:nth-child(${getColumnIndex(column)})`).textContent.trim();

            // Comparación numérica para campos específicos (por ejemplo, ID o salario)
            if (['employee_id', 'salary', 'age'].includes(column)) {
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

        // Reinsertar filas ordenadas
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
        const headers = document.querySelectorAll('#employeeReportTable thead th');
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].dataset.sort === sortColumn) {
                return i + 1;
            }
        }
        return 1;
    }

    // Manejar clics en encabezados con soporte para teclado
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
});
