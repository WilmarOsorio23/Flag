document.addEventListener('DOMContentLoaded', function () {

    const table = document.getElementById('clientesTarifasTable');
    if (table) {
        const headers = table.querySelectorAll('th.sortable');

        headers.forEach(header => {
            header.addEventListener('click', () => {
                const direction = header.getAttribute('data-direction') || 'asc';
                const newDirection = direction === 'asc' ? 'desc' : 'asc';

                sortTableByColumn(table, header, newDirection);

                // Resetear estados de otras columnas
                headers.forEach(h => h.setAttribute('data-direction', 'default'));
                header.setAttribute('data-direction', newDirection);
            });
        });

        function sortTableByColumn(table, header, direction) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentElement.children).indexOf(header);

            rows.sort((a, b) => {
                const cellA = a.cells[columnIndex].innerText.trim();
                const cellB = b.cells[columnIndex].innerText.trim();

                // Función de limpieza para números y moneda ($ 11,793 -> 11793)
                const cleanValue = (val) => {
                    let num = val.replace(/[$, ]/g, ''); 
                    return isNaN(num) || num === "" ? val.toLowerCase() : parseFloat(num);
                };

                const valA = cleanValue(cellA);
                const valB = cleanValue(cellB);

                if (typeof valA === 'number' && typeof valB === 'number') {
                    return direction === 'asc' ? valA - valB : valB - valA;
                }

                return direction === 'asc' 
                    ? valA.toString().localeCompare(valB.toString())
                    : valB.toString().localeCompare(valA.toString());
            });

            rows.forEach(row => tbody.appendChild(row));
        }
    }
    

    // ==========================================
    // SOPORTE PARA DROPDOWN DE AÑOS
    // ==========================================
    const anioBtn = document.getElementById('dropdownanios');
    const anioMenu = anioBtn ? anioBtn.nextElementSibling : null;

    if (anioBtn && anioMenu) {
        anioMenu.addEventListener('change', function () {
            const checked = anioMenu.querySelectorAll('input[type="checkbox"]:checked');
            if (checked.length > 0) {
                anioBtn.textContent = Array.from(checked).map(cb => cb.value).join(', ');
            } else {
                anioBtn.textContent = 'Seleccione años';
            }
        });
    }

    // ==========================================
    // LÓGICA DE REINICIO DE FILTROS
    // ==========================================
    const resetBtn = document.getElementById('btn-reset-filtros');
    const form = document.querySelector('form');
    const anioBtnn = document.getElementById('dropdownanios'); // El botón del dropdown

    if (resetBtn && form) {
        resetBtn.addEventListener('click', function () {
            
            // 1. Limpiar todos los inputs
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    input.checked = false; 
                } else {
                    input.value = ''; 
                }
            });

            // 2. Limpiar todos los selects 
            const selects = form.querySelectorAll('select');
            selects.forEach(select => {
                select.value = '';
            });

            // 3. Resetear el texto visual del dropdown de años
            if (anioBtnn) {
                anioBtnn.textContent = 'Seleccione años';
            }

            console.log("Campos del formulario limpiados visualmente.");
        });
    }

});