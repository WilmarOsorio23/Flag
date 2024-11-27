
   
    // Seleccionar todos los checkboxes
    document.getElementById('select-all').addEventListener('click', function(event) {
        let checkboxes = document.querySelectorAll('.row-select');
        for (let checkbox of checkboxes) {
            checkbox.checked = event.target.checked;
        }
    });

    // Confirmación antes de eliminar
    function confirmDelete() {
        let selected = document.querySelectorAll('.row-select:checked').length;
        if (selected === 0) {
            alert('No has seleccionado ningún elemento para eliminar.');
            return false;
        }
        return confirm('¿Estás seguro de que deseas eliminar los elementos seleccionados?');
    }

    // Habilitar edición en la fila seleccionada
    function enableEdit() {
        let selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            alert('No has seleccionado ningún IPC para editar.');
            return false;
        }
        if (selected.length > 1) {
            alert('Solo puedes editar un IPC a la vez.');
            return false;
        }

        let row = selected[0].closest('tr');
        let input = row.querySelector('[name ="Indice"]');
         input.classList.remove('form-control-plaintext');
         input.classList.add('form-control');
         input.readOnly = false;
         
        // Mostrar botón de guardar
        document.getElementById('save-button').classList.remove('d-none');
    }

    // Guardar los cambios en la fila seleccionada
    function saveRow() {
    
        let selected = document.querySelector('.row-select:checked');
        if (!selected) {
            alert('No has seleccionado ningún IPC para guardar.');
            return false;
        }
        let row = selected.closest('tr');
        let data={
            'Anio': row.querySelector('input[name ="Anio"]').value,
            'Mes': row.querySelector('input[name ="Mes"]').value,
            'Indice': row.querySelector('input[name ="Indice"]').value
        }
        console.log(data);
        let ipcId = selected.value;
      
        console.log(ipcId);
        // Enviar datos al servidor
        fetch(`/ipc/editar/${ipcId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify(data)
        })
        .then((response) => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Volver a modo de solo lectura
               const input = row.querySelector('input[name="Indice"]')

               input.classList.add('form-control-plaintext');
               input.classList.remove('form-control');
               

                // Ocultar botón de guardar 
                document.getElementById('save-button').classList.add('d-none');
            } else {
                alert('Error al guardar los cambios: ' + JSON.stringify(data.errors));
            }
        })
        .catch(error => {
            alert('Error al enviar los datos: ' + error.message);
        });

        return false;
    }

    // Clonar checkboxes seleccionados en el formulario de descarga
    document.getElementById('download-form').addEventListener('submit', function(event) {
        let selectedCheckboxes = document.querySelectorAll('.row-select:checked');
        if (selectedCheckboxes.length === 0) {
            alert('No has seleccionado ningún elemento para descargar.');
            event.preventDefault(); // Evita el envío si no hay elementos seleccionados
            return;
        }

        selectedCheckboxes.forEach(function(checkbox) {
            let clonedCheckbox = checkbox.cloneNode();
            clonedCheckbox.setAttribute('type', 'hidden'); // Ocultarlo en el formulario
            document.getElementById('download-form').appendChild(clonedCheckbox);
        });
    });
    

    // Prevenir la acción predeterminada al presionar Enter en cualquier parte de la página
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            // Verifica si el foco está en un botón o enlace específico
            let isButtonOrLink = event.target.tagName === 'BUTTON' || event.target.tagName === 'A';
            
            // Si no es un botón o enlace, previene el envío del formulario
            if (!isButtonOrLink) {
                event.preventDefault();
            }
        }
    });
