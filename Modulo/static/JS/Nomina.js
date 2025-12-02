// Modulo/static/JS/nomina.js
document.addEventListener('DOMContentLoaded', function () {
    // ============================
    // HELPERS
    // ============================
    function getCsrfToken() {
      return (
        (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value ||
        (document.querySelector('meta[name="csrf-token"]') || {}).getAttribute('content') ||
        ''
      );
    }
  
    // Atajo para mostrar mensajes inline (si existe message-box) o flotantes
    function inlineInfo(msg, type = 'info', elementId = 'message-box') {
      if (window.showInlineMessage) return window.showInlineMessage(msg, type, elementId);
      if (window.showMessage) return window.showMessage(msg, type);
      alert(`${type.toUpperCase()}: ${msg}`);
    }
  
    const csrfToken = getCsrfToken();
  
    // ============================
    // DESCARGA EXCEL
    // ============================
    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
      downloadForm.addEventListener('submit', function (event) {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
          inlineInfo('No has seleccionado ningún elemento para descargar.', 'warning');
          event.preventDefault();
          return;
        }
        const ids = Array.from(selected).map(cb => cb.value);
        document.getElementById('items_to_download').value = ids.join(',');
      });
    }
  
    // ============================
    // EDITAR / GUARDAR / CANCELAR
    // ============================
    window.saveRow = function () {
      const selected = document.querySelectorAll('.row-select:checked');
      if (selected.length !== 1) {
        inlineInfo('Debes seleccionar exactamente un registro para guardar.', 'danger');
        return;
      }
  
      const row = selected[0].closest('tr');
      const id = selected[0].value;
  
      const data = {
        Anio: row.querySelector('input[name="anio"]').value.trim(),
        Mes: row.querySelector('input[name="mes"]').value.trim(),
        Documento: row.querySelector('input[name="documento"]').value.trim(),
        Salario: row.querySelector('input[name="salario"]').value.trim(),
        Cliente: row.querySelector('select[name="Cliente"]').value.trim(),
      };
  
      if (!data.Anio || !data.Mes || !data.Documento || !data.Salario || !data.Cliente) {
        inlineInfo('Todos los campos son obligatorios.', 'danger');
        return;
      }
  
      // Mostrar “Guardando…”
      const savingToast = window.showFloatingMessage
        ? window.showFloatingMessage('Guardando...', 'info')
        : (window.showMessage && window.showMessage('Guardando...', 'info'));
  
      fetch(`/nomina/editar/${id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
      })
        .then(response =>
          response
            .json()
            .catch(() => ({}))
            .then(json => ({ ok: response.ok, json }))
        )
        .then(({ ok, json }) => {
          if (savingToast && typeof hideMessage === 'function') hideMessage(savingToast);
  
          if (!ok) {
            inlineInfo(`Error al guardar los cambios: ${json.error || 'Error desconocido'}`, 'danger');
            return;
          }
          if (json.status === 'success') {
            if (window.showSuccess) {
              window.showSuccess('Cambios guardados correctamente.');
            } else {
              inlineInfo('Cambios guardados correctamente.', 'success');
            }
            window.location.reload();
          } else {
            inlineInfo(`Error al guardar los cambios: ${json.error || 'Error desconocido'}`, 'danger');
          }
        })
        .catch(error => {
          if (savingToast && typeof hideMessage === 'function') hideMessage(savingToast);
          console.error('Error al guardar los cambios:', error);
          inlineInfo(`Error al guardar los cambios: ${error.message}`, 'danger');
        });
    };
  
    window.enableEdit = function () {
      const selected = document.querySelectorAll('.row-select:checked');
      if (selected.length === 0) {
        inlineInfo('No has seleccionado ningún registro para editar.', 'warning');
        return false;
      }
      if (selected.length > 1) {
        inlineInfo('Solo puedes editar un registro a la vez.', 'warning');
        return false;
      }
  
      const row = selected[0].closest('tr');
  
      const editableFields = [
        { name: 'salario', type: 'text' },
        { name: 'Cliente', type: 'select' },
      ];
  
      // Guardar originales
      editableFields.forEach(field => {
        const el = row.querySelector(`[name="${field.name}"]`);
        if (el && !el.hasAttribute('data-original-value')) {
          el.setAttribute('data-original-value', el.value);
        }
        const cell = row.querySelector(`[data-field="${field.name.toLowerCase()}"]`);
        const span = cell ? cell.querySelector('span.form-control-plaintext') : null;
        if (span && !span.hasAttribute('data-original-value')) {
          span.setAttribute('data-original-value', span.innerText.trim());
        }
      });
  
      // Activar edición
      editableFields.forEach(field => {
        const el = row.querySelector(`[name="${field.name}"]`);
        const cell = row.querySelector(`[data-field="${field.name.toLowerCase()}"]`);
        const span = cell ? cell.querySelector('span.form-control-plaintext') : null;
  
        if (el) {
          if (field.type === 'select') {
            el.disabled = false;
            el.classList.remove('form-control-plaintext');
            el.classList.add('form-control');
          } else {
            el.classList.remove('d-none', 'form-control-plaintext');
            el.classList.add('form-control');
            el.readOnly = false;
          }
        }
        if (span) span.classList.add('d-none');
      });
  
      // Deshabilitar selección global mientras se edita
      const selectAll = document.getElementById('select-all');
      if (selectAll) selectAll.disabled = true;
      document.querySelectorAll('.row-select').forEach(cb => (cb.disabled = true));
      selected[0].disabled = false;
  
      document.getElementById('edit-button').disabled = true;
      document.getElementById('save-button').classList.remove('d-none');
      document.getElementById('cancel-button').classList.remove('d-none');
    };
  
    window.cancelEdit = function () {
      const selected = document.querySelectorAll('.row-select:checked');
      if (selected.length !== 1) return;
  
      const row = selected[0].closest('tr');
      const editableFields = ['salario', 'Cliente'];
  
      editableFields.forEach(name => {
        const el = row.querySelector(`[name="${name}"]`);
        const cell = row.querySelector(`[data-field="${name.toLowerCase()}"]`);
        const span = cell ? cell.querySelector('span.form-control-plaintext') : null;
  
        if (el && el.hasAttribute('data-original-value')) {
          const original = el.getAttribute('data-original-value');
          el.value = original;
  
          if (name === 'Cliente') {
            el.disabled = true;
            el.classList.add('form-control-plaintext');
            el.classList.remove('form-control');
          } else {
            el.readOnly = true;
            el.classList.add('form-control-plaintext', 'd-none');
            el.classList.remove('form-control');
          }
        }
  
        if (span && span.hasAttribute('data-original-value')) {
          span.innerText = span.getAttribute('data-original-value');
          span.classList.remove('d-none');
        }
      });
  
      // Restaurar selección/botones
      const selectAll = document.getElementById('select-all');
      if (selectAll) selectAll.disabled = false;
      document.querySelectorAll('.row-select').forEach(cb => (cb.disabled = false));
      selected[0].checked = false;
  
      document.getElementById('edit-button').disabled = false;
      document.getElementById('save-button').classList.add('d-none');
      document.getElementById('cancel-button').classList.add('d-none');
    };
  
    // ============================
    // SELECT ALL
    // ============================
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
      selectAll.addEventListener('click', function (event) {
        const checked = event.target.checked;
        document.querySelectorAll('.row-select').forEach(cb => {
          cb.checked = checked;
        });
      });
    }
  
    // ============================
    // PREVENIR ENTER EN FORMULARIOS
    // ============================
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') event.preventDefault();
      });
    });
  
    // ============================
    // ELIMINACIÓN CON MODAL
    // ============================
    const deleteForm = document.getElementById('delete-form');
    const confirmDeleteModalEl = document.getElementById('confirmDeleteModal');
    const confirmDeleteButton = document.getElementById('confirm-delete-btn');
    const deleteButton = document.querySelector('.btn-outline-danger.fas.fa-trash-alt');
  
    if (deleteForm && confirmDeleteModalEl && confirmDeleteButton && deleteButton) {
      const confirmDeleteModal = new bootstrap.Modal(confirmDeleteModalEl);
  
      deleteButton.addEventListener('click', function (event) {
        event.preventDefault();
  
        const selectedIds = Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
        if (selectedIds.length === 0) {
          inlineInfo('No has seleccionado ningún elemento para eliminar.', 'warning');
          return;
        }
  
        confirmDeleteModal.show();
  
        confirmDeleteButton.onclick = async function () {
          const isRelated = await verifyRelations(selectedIds, csrfToken);
          if (isRelated) {
            inlineInfo(
              'Algunos elementos no pueden ser eliminados porque están relacionados con otras tablas.',
              'danger'
            );
            confirmDeleteModal.hide();
            if (selectAll) selectAll.checked = false;
            document.querySelectorAll('.row-select').forEach(cb => (cb.checked = false));
            return;
          }
  
          confirmDeleteModal.hide();
          deleteForm.submit();
        };
      });
    }
  
    // ============================
    // VERIFICAR RELACIONES
    // ============================
    async function verifyRelations(ids, csrfToken) {
      try {
        const response = await fetch('/nomina/verificar-relaciones/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ ids }),
        });
        const data = await response.json();
        return data.isRelated || false;
      } catch (error) {
        console.error('Error verificando relaciones:', error);
        // En caso de error, no bloqueamos la eliminación
        return false;
      }
    }
  
    // ============================
    // ORDENAMIENTO DE TABLA
    // ============================
    const table = document.querySelector('.table-primary');
    if (table) {
      const headers = table.querySelectorAll('th.sortable');
  
      headers.forEach(header => {
        header.addEventListener('click', () => {
          const column = header.getAttribute('data-sort');
          const direction = header.getAttribute('data-direction') || 'asc';
          const newDirection = direction === 'asc' ? 'desc' : 'asc';
  
          sortTableByColumn(table, column, newDirection);
  
          headers.forEach(h => {
            h.setAttribute('data-direction', 'default');
            const def = h.querySelector('.sort-icon-default');
            const asc = h.querySelector('.sort-icon-asc');
            const desc = h.querySelector('.sort-icon-desc');
            if (def) def.style.display = 'inline';
            if (asc) asc.style.display = 'none';
            if (desc) desc.style.display = 'none';
          });
  
          header.setAttribute('data-direction', newDirection);
          const def = header.querySelector('.sort-icon-default');
          const asc = header.querySelector('.sort-icon-asc');
          const desc = header.querySelector('.sort-icon-desc');
          if (def) def.style.display = 'none';
          if (asc && newDirection === 'asc') asc.style.display = 'inline';
          if (desc && newDirection === 'desc') desc.style.display = 'inline';
        });
      });
  
      function sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
  
        rows.sort((a, b) => {
          const cellA = a.querySelector(`[data-field="${columnName}"]`);
          const cellB = b.querySelector(`[data-field="${columnName}"]`);
          if (!cellA || !cellB) return 0;
  
          const getCellValue = cell => {
            const input = cell.querySelector('input');
            const span = cell.querySelector('span');
            const select = cell.querySelector('select');
            if (input && !input.classList.contains('d-none')) return input.value.trim();
            if (span && !span.classList.contains('d-none')) return span.innerText.trim();
            if (select) return select.options[select.selectedIndex].text.trim();
            return '';
          };
  
          const textA = getCellValue(cellA);
          const textB = getCellValue(cellB);
  
          if (['anio', 'mes', 'salario'].includes(columnName)) {
            const numA = parseFloat(textA.toString().replace(/[^\d.-]/g, '')) || 0;
            const numB = parseFloat(textB.toString().replace(/[^\d.-]/g, '')) || 0;
            return direction === 'asc' ? numA - numB : numB - numA;
          }
  
          return direction === 'asc'
            ? textA.localeCompare(textB)
            : textB.localeCompare(textA);
        });
  
        rows.forEach(row => tbody.appendChild(row));
      }
    }
  });
  