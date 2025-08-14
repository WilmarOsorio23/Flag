document.addEventListener('DOMContentLoaded', function () {
    function updateDropdownLabel(dropdownId, inputs) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(inputs).filter(input => 
            (input.type === 'radio' && input.checked) || 
            (input.type === 'checkbox' && input.checked)
        );
    
        if (selectedOptions.length === 0) {
            button.textContent = selectedText;
        } else if (selectedOptions.length === 1) {
            button.textContent = selectedOptions[0].nextSibling.textContent.trim();
        } else {
            button.textContent = `${selectedOptions.length} seleccionados`;
        }
    }
    
    function attachDropdownListeners(dropdownId) {
        const inputs = document.querySelectorAll(`#${dropdownId} ~ .dropdown-menu input[type="checkbox"], #${dropdownId} ~ .dropdown-menu input[type="radio"]`);
        inputs.forEach(input =>
            input.addEventListener('change', () => updateDropdownLabel(dropdownId, inputs))
        );
        updateDropdownLabel(dropdownId, inputs);
    }
    attachDropdownListeners('dropdownDocumento');
    attachDropdownListeners('dropdownAnio'); 
    attachDropdownListeners('dropdownLinea')
    attachDropdownListeners('dropdownMes')
    const table = document.getElementById('infoTiemposClienteTable');
if (table) {
    const headers = table.querySelectorAll('th.sortable');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.getAttribute('data-sort');
            const direction = header.getAttribute('data-direction') || 'asc';
            const newDirection = direction === 'asc' ? 'desc' : 'asc';

            sortTableByColumn(table, column, newDirection);

            // Reset all headers to default
            headers.forEach(h => {
                h.setAttribute('data-direction', 'default');
                h.querySelector('.sort-icon-default').style.display = 'inline';
                h.querySelector('.sort-icon-asc').style.display = 'none';
                h.querySelector('.sort-icon-desc').style.display = 'none';
            });
            
            // Set current header direction
            header.setAttribute('data-direction', newDirection);
            header.querySelector('.sort-icon-default').style.display = 'none';
            header.querySelector(`.sort-icon-${newDirection}`).style.display = 'inline';
        });
    });

    function sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Find column index by data-field attribute to be more precise
        const headerCells = Array.from(table.querySelectorAll('thead th'));
        const columnIndex = headerCells.findIndex(th => {
            return th.getAttribute('data-sort') === columnName;
        });
        
        if (columnIndex === -1) return; // Column not found

        rows.sort((a, b) => {
            // Find cells by data-field attribute for more reliable matching
            const cellA = a.querySelector(`td[data-field="${columnName}"]`);
            const cellB = b.querySelector(`td[data-field="${columnName}"]`);
            
            if (!cellA || !cellB) return 0;
            
            // Get the text content, handling different element types
            const getCellText = (cell) => {
                if (cell.querySelector('input, select')) {
                    return cell.querySelector('input, select').value.trim();
                }
                return cell.innerText.trim();
            };
            
            const textA = getCellText(cellA);
            const textB = getCellText(cellB);

            // Numeric comparison for specific columns
            if (columnName === 'horas' || columnName === 'horas_facturacion' || columnName === 'anio' || columnName === 'mes') {
                const numA = parseFloat(textA) || 0;
                const numB = parseFloat(textB) || 0;
                return direction === 'asc' ? numA - numB : numB - numA;
            }

            // Date comparison
            if (columnName.includes('fecha') || columnName.includes('fecha')) {
                const dateA = new Date(textA);
                const dateB = new Date(textB);
                if (!isNaN(dateA) && !isNaN(dateB)) {
                    return direction === 'asc' ? dateA - dateB : dateB - dateA;
                }
            }

            // String comparison
            return direction === 'asc' 
                ? textA.localeCompare(textB) 
                : textB.localeCompare(textA);
        });

        // Reattach sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
}  
});