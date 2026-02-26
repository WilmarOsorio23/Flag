document.addEventListener('DOMContentLoaded', function() {
    
    
    // Años 
    const aniosCheckboxes = document.querySelectorAll('#dropdownanios ~ .dropdown-menu input[type="checkbox"]');
    aniosCheckboxes.forEach((checkbox) =>
        checkbox.addEventListener('change', () =>
            updateDropdownLabel('dropdownanios', aniosCheckboxes)
        )
    );

      // =============================
      // LÓGICA PARA BOTÓN "OTROS SÍ"
      // =============================

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

                const url = `/Informes/informes_otros_si/?Nombre_Cliente=${encodeURIComponent(cliente)}&Contrato=${encodeURIComponent(contrato)}&ContratoVigente=${contratoVigente}`;
  

                window.open(url, '_blank');
            });
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

});
