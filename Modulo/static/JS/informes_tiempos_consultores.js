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

});