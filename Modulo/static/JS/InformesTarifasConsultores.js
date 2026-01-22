document.addEventListener('DOMContentLoaded', function() {
    
    //  =============================
    //  LÓGICA DE ORDENAMIENTO DE TABLA
    //  =============================
    const table = document.getElementById('consultoresTarifasTable');
    if (table) {
        const headers = table.querySelectorAll('th.sortable');

        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.getAttribute('data-sort');
                const direction = header.getAttribute('data-direction') || 'asc';
                const newDirection = direction === 'asc' ? 'desc' : 'asc';

                sortTableByColumn(table, header, newDirection);

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

    // =============================
    // SOPORTE PARA DROPDOWN DE AÑOS (igual que Mes)
    // =============================
    const anioDropdownBtn = document.getElementById('dropdownAnio');
    const anioDropdownMenu = anioDropdownBtn ? anioDropdownBtn.nextElementSibling : null;
    if (anioDropdownBtn && anioDropdownMenu) {
        anioDropdownMenu.addEventListener('change', function () {
            const checked = anioDropdownMenu.querySelectorAll('input[type="checkbox"]:checked');
            if (checked.length > 0) {
                anioDropdownBtn.textContent = Array.from(checked).map(cb => cb.value).join(', ');
            } else {
                anioDropdownBtn.textContent = 'Seleccione Años';
            }
        });
        // Para que funcione al hacer click en el checkbox
        anioDropdownMenu.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function () {
                const checked = anioDropdownMenu.querySelectorAll('input[type="checkbox"]:checked');
                if (checked.length > 0) {
                    anioDropdownBtn.textContent = Array.from(checked).map(cb => cb.value).join(', ');
                } else {
                    anioDropdownBtn.textContent = 'Seleccione Años';
                }
            });
        });
    }

});
