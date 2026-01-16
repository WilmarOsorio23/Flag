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

    const salarioEl = row.querySelector('input[name="salario"]');
    const clienteEl = row.querySelector('select[name="Cliente"]');

    const data = {
      Salario: (salarioEl ? salarioEl.value.trim() : ''),
      Cliente: (clienteEl ? clienteEl.value.trim() : ''),
    };

    if (!data.Salario || !data.Cliente) {
      inlineInfo('Salario y Cliente son obligatorios.', 'danger');
      return;
    }

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
          if (window.showSuccess) window.showSuccess('Cambios guardados correctamente.');
          else inlineInfo('Cambios guardados correctamente.', 'success');
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
      return false;
    }
  }

  // =========================================================
  // NUEVO: BULK COPY MODAL (preview + create)
  // =========================================================
  const bulkLoadBtn = document.getElementById('bulk-load-btn');
  const bulkCreateBtn = document.getElementById('bulk-create-btn');
  const bulkPreviewBody = document.getElementById('bulk-preview-body');
  const bulkSummary = document.getElementById('bulk-summary');
  const bulkClientTemplate = document.getElementById('bulk-client-template');
  const bulkSelectAll = document.getElementById('bulk-select-all');

  const originYearEl = document.getElementById('bulk-origin-year');
  const originMonthEl = document.getElementById('bulk-origin-month');
  const destYearEl = document.getElementById('bulk-dest-year');
  const destMonthEl = document.getElementById('bulk-dest-month');
  const bulkModeEl = document.getElementById('bulk-mode');

  function getClientOptionsHTML() {
    return bulkClientTemplate ? bulkClientTemplate.innerHTML : '';
  }

  function renderBulkRows(items) {
    const optionsHTML = getClientOptionsHTML();
    if (!items || items.length === 0) {
      bulkPreviewBody.innerHTML = `<tr><td colspan="4" class="text-muted">No hay registros en el origen.</td></tr>`;
      bulkCreateBtn.disabled = true;
      return;
    }

    bulkPreviewBody.innerHTML = items.map((it) => {
      const empLabel = `
        <div class="fw-semibold">${escapeHtml(it.empleado_nombre || '')}</div>
        <div class="text-muted small">${escapeHtml(it.empleado_documento || '')}</div>
      `;

      return `
        <tr data-empleado-id="${it.empleado_id}">
          <td><input type="checkbox" class="bulk-row-check" checked></td>
          <td>${empLabel}</td>
          <td>
            <input type="text" class="form-control form-control-sm bulk-salario" value="${escapeAttr(it.salario || '')}">
          </td>
          <td>
            <select class="form-select form-select-sm bulk-cliente">
              ${optionsHTML}
            </select>
          </td>
        </tr>
      `;
    }).join('');

    // set selected client after insert
    bulkPreviewBody.querySelectorAll('tr').forEach((tr, idx) => {
      const sel = tr.querySelector('.bulk-cliente');
      if (sel && items[idx] && items[idx].cliente_id != null) {
        sel.value = String(items[idx].cliente_id);
      }
    });

    bulkCreateBtn.disabled = false;
    if (bulkSelectAll) bulkSelectAll.checked = true;

    bulkSummary.textContent = `Filas cargadas: ${items.length}. Puedes ajustar salario/cliente por fila antes de crear.`;
  }

  function escapeHtml(str) {
    return String(str ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }
  function escapeAttr(str) {
    return escapeHtml(str).replaceAll('\n', ' ').replaceAll('\r', ' ');
  }

  if (bulkSelectAll) {
    bulkSelectAll.addEventListener('change', () => {
      const checked = bulkSelectAll.checked;
      bulkPreviewBody.querySelectorAll('.bulk-row-check').forEach(cb => cb.checked = checked);
    });
  }

  if (bulkLoadBtn) {
    bulkLoadBtn.addEventListener('click', async () => {
      const anio = (originYearEl?.value || '').trim();
      const mes = (originMonthEl?.value || '').trim();
      if (!anio || !mes) {
        inlineInfo('Debes ingresar Año y Mes de origen.', 'warning');
        return;
      }

      bulkPreviewBody.innerHTML = `<tr><td colspan="4" class="text-muted">Cargando...</td></tr>`;
      bulkSummary.textContent = '';

      try {
        const res = await fetch('/nomina/bulk/preview/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ anio, mes }),
        });

        const json = await res.json().catch(() => ({}));
        if (!res.ok) {
          inlineInfo(json.error || 'Error cargando origen.', 'danger');
          bulkPreviewBody.innerHTML = `<tr><td colspan="4" class="text-muted">Error.</td></tr>`;
          bulkCreateBtn.disabled = true;
          return;
        }

        renderBulkRows(json.items || []);
      } catch (e) {
        console.error(e);
        inlineInfo(`Error cargando origen: ${e.message}`, 'danger');
        bulkPreviewBody.innerHTML = `<tr><td colspan="4" class="text-muted">Error.</td></tr>`;
        bulkCreateBtn.disabled = true;
      }
    });
  }

  if (bulkCreateBtn) {
    bulkCreateBtn.addEventListener('click', async () => {
      const d_anio = (destYearEl?.value || '').trim();
      const d_mes = (destMonthEl?.value || '').trim();
      const o_anio = (originYearEl?.value || '').trim();
      const o_mes = (originMonthEl?.value || '').trim();
      const mode = (bulkModeEl?.value || 'skip').trim();

      if (!o_anio || !o_mes) {
        inlineInfo('Primero carga un origen.', 'warning');
        return;
      }
      if (!d_anio || !d_mes) {
        inlineInfo('Debes ingresar Año y Mes de destino.', 'warning');
        return;
      }

      const rows = Array.from(bulkPreviewBody.querySelectorAll('tr'));
      const items = rows
        .filter(tr => tr.querySelector('.bulk-row-check')?.checked)
        .map(tr => ({
          empleado_id: tr.getAttribute('data-empleado-id'),
          salario: tr.querySelector('.bulk-salario')?.value?.trim() || '',
          cliente_id: tr.querySelector('.bulk-cliente')?.value || '',
        }));

      if (items.length === 0) {
        inlineInfo('No hay filas seleccionadas para crear.', 'warning');
        return;
      }

      const savingToast = window.showFloatingMessage
        ? window.showFloatingMessage('Creando registros...', 'info')
        : (window.showMessage && window.showMessage('Creando registros...', 'info'));

      try {
        const res = await fetch('/nomina/bulk/create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({
            origen: { anio: o_anio, mes: o_mes },
            destino: { anio: d_anio, mes: d_mes },
            mode,
            items,
          }),
        });

        const json = await res.json().catch(() => ({}));
        if (savingToast && typeof hideMessage === 'function') hideMessage(savingToast);

        if (!res.ok) {
          inlineInfo(json.error || 'Error en creación masiva.', 'danger');
          return;
        }

        const errs = (json.errors || []);
        const msg =
          `Listo. Creados: ${json.created || 0}, ` +
          `Actualizados: ${json.updated || 0}, ` +
          `Omitidos: ${json.skipped || 0}.` +
          (errs.length ? ` Errores: ${errs.length} (revisa consola).` : '');

        if (errs.length) console.warn('Errores bulk:', errs);

        if (window.showSuccess) window.showSuccess(msg);
        else inlineInfo(msg, 'success');

        window.location.reload();
      } catch (e) {
        if (savingToast && typeof hideMessage === 'function') hideMessage(savingToast);
        console.error(e);
        inlineInfo(`Error en creación masiva: ${e.message}`, 'danger');
      }
    });
  }
});
