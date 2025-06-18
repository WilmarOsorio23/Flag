document.addEventListener('DOMContentLoaded', function() {
    // Función de ordenamiento mejorada
    function sortTable(column, direction) {
        const table = document.getElementById('clientesContratosTable');
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
        const headers = document.querySelectorAll('#clientesContratosTable thead th');
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

    // Años 
    const aniosCheckboxes = document.querySelectorAll('#dropdownanios ~ .dropdown-menu input[type="checkbox"]');
    aniosCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownanios', aniosCheckboxes)
        )
    );

      // Botón "Otros Sí" para abrir informe con filtros desde registro seleccionado
        const otrosSiBtn = document.getElementById('otrosSi-button');
       
        if (otrosSiBtn) {
            otrosSiBtn.addEventListener('click', function () {
                const selectedCheckboxes = document.querySelectorAll('.row-select:checked');

                if (selectedCheckboxes.length !== 1) {
                    alert('Debes seleccionar exactamente un contrato para ver sus Otros Sí.');
                    return;
                }

                const selectedRow = selectedCheckboxes[0].closest('tr');
                const cells = selectedRow.querySelectorAll('td');

                const cliente = cells[2].textContent.trim();         // Nombre Cliente
                const contrato = cells[3].textContent.trim();        // Contrato
                const vigenteText = cells[8].textContent.trim();     // Contrato Vigente (col 8)
                const contratoVigente = vigenteText.trim().toLowerCase() === 'si' ? 'True' : 'False';

                const url = `/informes/informes_otros_si/?Nombre_Cliente=${encodeURIComponent(cliente)}&Contrato=${encodeURIComponent(contrato)}&ContratoVigente=${contratoVigente}`;
  

                window.open(url, '_blank');
            });
        }

    // =============================
    // LÓGICA DE REINICIO DE FILTROS
    // =============================
    const resetBtn = document.getElementById('btn-reset-filtros');
    const form = document.querySelector('form');

    if (resetBtn && form) {
        console.log('✔ Botón de reinicio y formulario encontrados');

        resetBtn.addEventListener('click', function () {
        console.log('🔄 Botón de reinicio clickeado');

        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            console.log(`↩ Reiniciando select: ${select.name}`);
            select.value = '';
        });

        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            console.log(`↩ Limpiando input: ${input.name}`);
            input.value = '';
        });
        });
    } else {
        if (!resetBtn) console.error('❌ No se encontró el botón con id="btn-reset-filtros"');
        if (!form) console.error('❌ No se encontró ningún formulario');
    }
});
