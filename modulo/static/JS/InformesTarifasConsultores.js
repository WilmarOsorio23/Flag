document.addEventListener('DOMContentLoaded', function() {

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
