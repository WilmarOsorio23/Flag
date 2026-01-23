document.addEventListener('DOMContentLoaded', function() {

    // ==========================
    // CSRF
    // ==========================
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  
    // ==========================
    // DOWNLOAD: enviar solo IDs seleccionados (sin clonar checkbox con atributo form)
    // ==========================
    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
      downloadForm.addEventListener('submit', function(event) {
        // Limpia clones previos
        this.querySelectorAll('input[data-clone="1"]').forEach(n => n.remove());
  
        const selectedCheckboxes = document.querySelectorAll('.row-select:checked');
        if (selectedCheckboxes.length === 0) {
          alert('No has seleccionado ningún elemento para descargar.');
          event.preventDefault();
          return;
        }
  
        selectedCheckboxes.forEach(cb => {
          const hidden = document.createElement('input');
          hidden.type = 'hidden';
          hidden.name = 'items_to_delete';
          hidden.value = cb.value;
          hidden.setAttribute('data-clone', '1');
          this.appendChild(hidden);
        });
      });
    }
  
    // ==========================
    // SAVE ROW (editar inline)
    // ==========================
    window.saveRow = function() {
      let selected = document.querySelectorAll('.row-select:checked');
      if (selected.length !== 1) {
        showError('Error al guardar: No hay un detalle seleccionado.');
        return;
      }
  
      let row = selected[0].closest('tr');
  
      let data = {
        'valorHora': row.querySelector('input[name="valorHora"]').value,
        'valorDia': row.querySelector('input[name="valorDia"]').value,
        'valorMes': row.querySelector('input[name="valorMes"]').value,
        'monedaId': row.querySelector('select[name="moneda"]').value,
        'moduloId': row.querySelector('select[name="moduloId"]').value,
        'iva': row.querySelector('input[name="iva"]').value.trim() || null,
        'rteFte': row.querySelector('input[name="rteFte"]').value.trim() || null,
      };
  
      let idd = selected[0].value;
  
      // Deshabilitar checkboxes y botón de edición
      document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
      document.getElementById('edit-button').disabled = true;
  
      fetch(`/tarifa_consultores/editar/${idd}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
      })
      .then(response => {
        if (!response.ok) throw new Error('Error al guardar los cambios');
        return response.json();
      })
      .then(res => {
        if (res.status === 'success') {
          showSuccess('Cambios guardados correctamente.');
          window.location.reload();
          disableEditMode(selected, row);
        } else {
          showError('Error al guardar los cambios: ' + (res.error || 'Error desconocido'));
          restoreOriginalValues(row);
          disableEditMode(selected, row);
        }
      })
      .catch(error => {
        console.error('Error al guardar los cambios:', error);
        showError('Error al guardar los cambios: ' + error.message);
        restoreOriginalValues(row);
        disableEditMode(selected, row);
      });
    };
  
    // ==========================
    // ENABLE EDIT
    // ==========================
    window.enableEdit = function() {
      const selected = document.querySelectorAll('.row-select:checked');
      if (selected.length === 0) {
        showError('No has seleccionado ningún registro para editar.');
        return false;
      }
      if (selected.length > 1) {
        showError('Solo puedes editar un registro a la vez.');
        return false;
      }
  
      const row = selected[0].closest('tr');
  
      const editableFields = [
        { name: "rteFte", type: "text" },
        { name: "valorHora", type: "text" },
        { name: "valorDia", type: "text" },
        { name: "valorMes", type: "text" },
        { name: "moduloId", type: "select" },
        { name: "iva", type: "text" },
        { name: "moneda", type: "select" }
      ];
  
      // Guardar valores originales
      editableFields.forEach(field => {
        const element = row.querySelector(`[name="${field.name}"]`);
        const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
        if (element) element.setAttribute('data-original-value', element.value);
        if (span) span.setAttribute('data-original-value', span.innerText.trim());
      });
  
      // Mostrar inputs/selects y ocultar spans
      editableFields.forEach(field => {
        const element = row.querySelector(`[name="${field.name}"]`);
        const span = row.querySelector(`[data-field="${field.name}"] span.form-control-plaintext`);
  
        if (element) {
          if (field.type === "select") {
            element.disabled = false;
            element.classList.remove('form-control-plaintext');
            element.classList.remove('d-none');
            element.classList.add('form-control');
          } else {
            element.classList.remove('d-none');
            element.classList.remove('form-control-plaintext');
            element.classList.add('form-control');
            element.readOnly = false;
          }
        }
        if (span) span.classList.add('d-none');
      });
  
      // Bloquear selección múltiple mientras edita
      document.getElementById('select-all').disabled = true;
      document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = true);
      selected[0].disabled = false; // mantener el que está seleccionado usable
      document.getElementById('edit-button').disabled = true;
  
      // Mostrar botones guardar/cancelar
      document.getElementById('save-button').classList.remove('d-none');
      document.getElementById('cancel-button').classList.remove('d-none');
    };
  
    // ==========================
    // CANCEL EDIT
    // ==========================
    window.cancelEdit = function() {
      const selected = document.querySelectorAll('.row-select:checked');
      if (selected.length !== 1) return;
  
      const row = selected[0].closest('tr');
      const editableFields = ["valorHora", "valorDia", "valorMes", "rteFte", "iva", "moneda", "moduloId"];
  
      editableFields.forEach(name => {
        const element = row.querySelector(`[name="${name}"]`);
        const span = row.querySelector(`[data-field="${name}"] span.form-control-plaintext`);
  
        if (element) {
          if (element.tagName === "SELECT") {
            element.value = element.getAttribute('data-original-value');
            element.disabled = true;
            element.classList.add('d-none');
          } else {
            element.value = element.getAttribute('data-original-value');
            element.readOnly = true;
            element.classList.add('d-none');
          }
        }
        if (span) {
          span.innerText = span.getAttribute('data-original-value');
          span.classList.remove('d-none');
        }
      });
  
      document.getElementById('select-all').disabled = false;
      document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = false);
      document.getElementById('edit-button').disabled = false;
  
      document.getElementById('save-button').classList.add('d-none');
      document.getElementById('cancel-button').classList.add('d-none');
    };
  
    // ==========================
    // Prevent enter submit
    // ==========================
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('keydown', function(event) {
        if (event.key === "Enter") event.preventDefault();
      });
    });
  
    // ==========================
    // Delete modal flow
    // ==========================
    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteModalEl = document.getElementById('confirmDeleteModal');
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');
  
    const confirmDeleteModal = confirmDeleteModalEl ? new bootstrap.Modal(confirmDeleteModalEl) : null;
  
    // select all
    document.getElementById('select-all')?.addEventListener('click', function(event) {
      const checkboxes = document.querySelectorAll('.row-select');
      checkboxes.forEach(cb => cb.checked = event.target.checked);
    });
  
    function getSelectedIds() {
      return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }
  
    document.querySelector('.btn-outline-danger.fas.fa-trash-alt')?.addEventListener('click', function(event) {
      event.preventDefault();
  
      const selectedIds = getSelectedIds();
      if (selectedIds.length === 0) {
        showError('No has seleccionado ningún elemento para eliminar.');
        return;
      }
  
      confirmDeleteModal?.show();
  
      confirmDeleteButton.onclick = function() {
        // ✅ Como los checkboxes tienen form="delete-form", al enviar deleteForm viajan SOLO esos campos.
        deleteForm.submit();
      };
    });
  
    // ==========================
    // Helpers (ya los tienes en tu proyecto, aquí quedan como fallback)
    // ==========================
    function disableEditMode(selected, row) {
      row.querySelectorAll('input.form-control').forEach(input => {
        input.classList.add('form-control-plaintext');
        input.classList.remove('form-control');
        input.readOnly = true;
        input.classList.add('d-none');
      });
  
      row.querySelectorAll('select').forEach(select => {
        select.disabled = true;
        if (select.classList.contains('form-control')) {
          select.classList.add('d-none');
        }
      });
  
      selected[0].checked = false;
      selected[0].disabled = false;
  
      document.getElementById('select-all').disabled = false;
      document.querySelectorAll('.row-select').forEach(checkbox => checkbox.disabled = false);
      document.getElementById('edit-button').disabled = false;
  
      document.getElementById('save-button').classList.add('d-none');
      document.getElementById('cancel-button').classList.add('d-none');
    }
  
    function restoreOriginalValues(row) {
      row.querySelectorAll('input').forEach(input => {
        if (input.hasAttribute('data-original-value')) {
          input.value = input.getAttribute('data-original-value');
        }
      });
  
      row.querySelectorAll('select').forEach(select => {
        if (select.hasAttribute('data-original-value')) {
          select.value = select.getAttribute('data-original-value');
        }
      });
    }
  
  });
  