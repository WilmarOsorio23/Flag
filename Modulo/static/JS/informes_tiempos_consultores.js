document.addEventListener('DOMContentLoaded', function () {
    // ===========================
    // LÓGICA DROPDOWNS MULTI-SELECT
    // ===========================
    function updateDropdownLabel(dropdownId, inputs) {
      const button = document.getElementById(dropdownId);
      if (!button) return;
  
      const selectedText = button.getAttribute('data-selected-text') || 'Seleccione';
      const selectedOptions = Array.from(inputs).filter(input =>
        (input.type === 'radio' && input.checked) ||
        (input.type === 'checkbox' && input.checked)
      );
  
      if (selectedOptions.length === 0) {
        button.textContent = selectedText;
      } else if (selectedOptions.length === 1) {
        const input = selectedOptions[0];
        // Texto de la etiqueta asociada
        const labelText = input.parentNode
          ? input.parentNode.textContent.trim()
          : input.nextSibling
          ? input.nextSibling.textContent.trim()
          : selectedText;
        button.textContent = labelText;
      } else {
        button.textContent = `${selectedOptions.length} seleccionados`;
      }
    }
  
    function attachDropdownListeners(dropdownId) {
      const button = document.getElementById(dropdownId);
      if (!button) return;
  
      const selector = `#${dropdownId} ~ .dropdown-menu input[type="checkbox"], #${dropdownId} ~ .dropdown-menu input[type="radio"]`;
      const inputs = document.querySelectorAll(selector);
  
      inputs.forEach(input => {
        input.addEventListener('change', () => updateDropdownLabel(dropdownId, inputs));
      });
  
      updateDropdownLabel(dropdownId, inputs);
    }
  
    attachDropdownListeners('dropdownDocumento');
    attachDropdownListeners('dropdownAnio');
    attachDropdownListeners('dropdownLinea');
    attachDropdownListeners('dropdownMes');
  
    // ===========================
    // LÓGICA ORDENAMIENTO TABLA
    // ===========================
    const table = document.getElementById('infoTiemposClienteTable');
    if (table) {
      const headers = table.querySelectorAll('th.sortable');
  
      headers.forEach(header => {
        header.dataset.direction = header.dataset.direction || 'default';
  
        header.addEventListener('click', () => {
          const column = header.getAttribute('data-sort');
          const direction = header.getAttribute('data-direction') || 'asc';
          const newDirection = direction === 'asc' ? 'desc' : 'asc';
  
          sortTableByColumn(table, column, newDirection);
  
          // Reset todos los headers
          headers.forEach(h => {
            h.setAttribute('data-direction', 'default');
            const iconDefault = h.querySelector('.sort-icon-default');
            const iconAsc = h.querySelector('.sort-icon-asc');
            const iconDesc = h.querySelector('.sort-icon-desc');
            if (iconDefault) iconDefault.style.display = 'inline';
            if (iconAsc) iconAsc.style.display = 'none';
            if (iconDesc) iconDesc.style.display = 'none';
          });
  
          // Set íconos del header actual
          header.setAttribute('data-direction', newDirection);
          const iconDefault = header.querySelector('.sort-icon-default');
          const iconAsc = header.querySelector('.sort-icon-asc');
          const iconDesc = header.querySelector('.sort-icon-desc');
          if (iconDefault) iconDefault.style.display = 'none';
          if (iconAsc && newDirection === 'asc') iconAsc.style.display = 'inline';
          if (iconDesc && newDirection === 'desc') iconDesc.style.display = 'inline';
        });
      });
  
      function sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
  
        // Verificar que la columna exista
        const headerCells = Array.from(table.querySelectorAll('thead th'));
        const columnIndex = headerCells.findIndex(th => {
          return th.getAttribute('data-sort') === columnName;
        });
        if (columnIndex === -1) return;
  
        const getCellText = cell => {
          if (!cell) return '';
          const inputOrSelect = cell.querySelector('input, select');
          if (inputOrSelect) {
            return (inputOrSelect.value || '').trim();
          }
          return (cell.innerText || '').trim();
        };
  
        rows.sort((a, b) => {
          const cellA = a.querySelector(`td[data-field="${columnName}"]`);
          const cellB = b.querySelector(`td[data-field="${columnName}"]`);
  
          if (!cellA || !cellB) return 0;
  
          const textA = getCellText(cellA);
          const textB = getCellText(cellB);
  
          // Comparación numérica para horas, horas de facturación, año, mes
          if (
            columnName === 'horas' ||
            columnName === 'anio' ||
            columnName === 'mes' ||
            columnName.startsWith('horas_facturacion')
          ) {
            const numA = parseFloat(textA.replace(',', '.')) || 0;
            const numB = parseFloat(textB.replace(',', '.')) || 0;
            return direction === 'asc' ? numA - numB : numB - numA;
          }
  
          // Comparación de fecha si el nombre de la columna lo sugiere
          if (columnName.includes('fecha')) {
            const dateA = new Date(textA);
            const dateB = new Date(textB);
            if (!isNaN(dateA) && !isNaN(dateB)) {
              return direction === 'asc' ? dateA - dateB : dateB - dateA;
            }
          }
  
          // Comparación de texto (string)
          if (direction === 'asc') {
            return textA.localeCompare(textB);
          }
          return textB.localeCompare(textA);
        });
  
        rows.forEach(row => tbody.appendChild(row));
      }
    }
  });
  