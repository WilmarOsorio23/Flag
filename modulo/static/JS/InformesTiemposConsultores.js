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
  
  });
  