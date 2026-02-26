document.addEventListener('DOMContentLoaded', function () {

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