document.addEventListener('DOMContentLoaded', function () {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  window.cancelEdit = function () {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 1) {
      window.location.reload();
      window.showMessage('Cambios cancelados.', 'warning');
    } else {
      window.showMessage('Selecciona 1 registro para cancelar edición.', 'danger');
    }
  };

  document.getElementById('download-form').addEventListener('submit', function (event) {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) {
      window.showMessage('No has seleccionado ningún elemento para descargar.', 'danger');
      event.preventDefault();
      return;
    }
    const ids = Array.from(selected).map(chk => chk.value);
    document.getElementById('items_to_download').value = ids.join(',');
  });

  window.enableEdit = function () {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) return window.showMessage('Selecciona un registro para editar.', 'warning');
    if (selected.length > 1) return window.showMessage('Solo puedes editar un registro a la vez.', 'warning');

    const row = selected[0].closest('tr');

    document.getElementById('select-all').disabled = true;
    document.querySelectorAll('.row-select').forEach(chk => chk.disabled = true);
    document.getElementById('edit-button').disabled = true;

    row.querySelectorAll('td[data-field]').forEach(td => {
      const span = td.querySelector('span.cell-text');
      const sel = td.querySelector('select');
      if (span && sel) {
        sel.setAttribute('data-original-value', sel.value);
        span.classList.add('d-none');
        sel.classList.remove('d-none');
      }
    });

    document.getElementById('save-button').classList.remove('d-none');
    document.getElementById('cancel-button').classList.remove('d-none');
  };

  window.saveRow = function () {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length !== 1) {
      return window.showMessage('Error: selecciona exactamente 1 registro para guardar.', 'danger');
    }

    const row = selected[0].closest('tr');
    const id = selected[0].value;

    const lineaId = row.querySelector('select[name="LineaId"]').value;
    const clienteId = row.querySelector('select[name="ClienteId"]').value;
    const moduloId = row.querySelector('select[name="ModuloId"]').value;
    const centroCostoId = row.querySelector('select[name="CentroCostoId"]').value;

    const payload = { LineaId: lineaId, ClienteId: clienteId, ModuloId: moduloId, CentroCostoId: centroCostoId };

    fetch(`/linea_cliente_centrocostos/editar/${id}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(payload)
    })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || 'Error al guardar los cambios');
        return data;
      })
      .then((data) => {
        if (data.status === 'success') {
          window.showMessage('Cambios guardados correctamente.', 'success');
          window.location.reload();
        } else {
          window.showMessage(data.error || 'Error desconocido', 'danger');
        }
      })
      .catch((err) => window.showMessage(err.message, 'danger'));
  };

  document.getElementById('select-all').addEventListener('click', function (event) {
    document.querySelectorAll('.row-select').forEach(chk => chk.checked = event.target.checked);
  });

  // Eliminar con confirmación + verifyRelations
  const deleteForm = document.getElementById('delete-form');
  const confirmDeleteModalEl = document.getElementById('confirmDeleteModal');
  const modal = new bootstrap.Modal(confirmDeleteModalEl);
  const confirmDeleteButton = document.getElementById('confirm-delete-btn');

  function getSelectedIds() {
    return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
  }

  async function verifyRelations(ids) {
    try {
      const response = await fetch('verificar-relaciones/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ ids })
      });
      const data = await response.json();
      return data.isRelated || false;
    } catch (e) {
      console.error(e);
      return true;
    }
  }

  document.querySelector('.btn-outline-danger.fas.fa-trash-alt')
    .addEventListener('click', async function (event) {
      event.preventDefault();
      const ids = getSelectedIds();

      if (ids.length === 0) return window.showMessage('No has seleccionado ningún elemento para eliminar.', 'danger');

      modal.show();

      confirmDeleteButton.onclick = async function () {
        const isRelated = await verifyRelations(ids);
        if (isRelated) {
          window.showMessage('Algunos registros no pueden eliminarse porque están relacionados con otras tablas.', 'danger');
          modal.hide();
          document.getElementById('select-all').checked = false;
          document.querySelectorAll('.row-select').forEach(chk => chk.checked = false);
          return;
        }
        deleteForm.submit();
      };
    });

  // Sorting
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
          h.querySelector('.sort-icon-default').style.display = 'inline';
          h.querySelector('.sort-icon-asc').style.display = 'none';
          h.querySelector('.sort-icon-desc').style.display = 'none';
        });

        header.setAttribute('data-direction', newDirection);
        header.querySelector('.sort-icon-default').style.display = 'none';
        header.querySelector(`.sort-icon-${newDirection}`).style.display = 'inline';
      });
    });

    function sortTableByColumn(table, columnName, direction) {
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((a, b) => {
        const cellA = a.querySelector(`[data-field="${columnName}"]`);
        const cellB = b.querySelector(`[data-field="${columnName}"]`);
        if (!cellA || !cellB) return 0;

        const getCellValue = (cell) => {
          const select = cell.querySelector('select');
          const span = cell.querySelector('span');
          if (select && !select.classList.contains('d-none')) {
            return select.options[select.selectedIndex]?.text?.trim() || '';
          }
          if (span) return span.innerText.trim();
          return '';
        };

        const textA = getCellValue(cellA);
        const textB = getCellValue(cellB);

        return direction === 'asc'
          ? textA.localeCompare(textB)
          : textB.localeCompare(textA);
      });

      rows.forEach(row => tbody.appendChild(row));
    }
  }
});
