class EmpleadoManager {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        this.deleteForm = document.getElementById('delete-form');
        this.confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        this.confirmDeleteButton = document.getElementById('confirm-delete-btn');
        this.init();
    }

    init() {
        this.preventFormSubmissionOnEnter();
        this.setupEventListeners();
        this.setupTableSorting();
    }

    preventFormSubmissionOnEnter() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('keydown', (event) => {
                if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        });
    }

    setupEventListeners() {
        document.getElementById("select-all").addEventListener("change", (e) => {
            this.toggleAllCheckboxes(e.target.checked);
        });

        document.querySelector('.btn-outline-danger.fas.fa-trash-alt').addEventListener('click', (e) => {
            this.handleDeleteConfirmation(e);
        });
    }

    toggleAllCheckboxes(checked) {
        document.querySelectorAll(".row-select").forEach(cb => cb.checked = checked);
    }

    async handleDeleteConfirmation(event) {
        event.preventDefault();
        const selectedIds = this.getSelectedIds();
        
        if (selectedIds.length === 0) {
            this.showMessage('No has seleccionado ningún elemento para eliminar.', 'danger');
            return;
        }

        this.confirmDeleteModal.show();
        
        this.confirmDeleteButton.onclick = async () => {
            const isRelated = await this.verifyRelations(selectedIds);
            if (isRelated) {
                this.showMessage('Algunos elementos no pueden ser eliminados porque están relacionados con otras tablas.', 'danger');
                this.confirmDeleteModal.hide();
                this.resetCheckboxes();
                return;
            }

            document.getElementById('items_to_delete').value = selectedIds.join(',');
            this.deleteForm.submit();
        };
    }

    getSelectedIds() {
        return Array.from(document.querySelectorAll('.row-select:checked')).map(el => el.value);
    }

    resetCheckboxes() {
        document.getElementById('select-all').checked = false;
        document.querySelectorAll('.row-select').forEach(checkbox => checkbox.checked = false);
    }

    async verifyRelations(ids) {
        try {
            const response = await fetch('/empleado/verificar-relaciones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({ ids }),
            });
            const data = await response.json();
            return data.isRelated || false;
        } catch (error) {
            console.error('Error verificando relaciones:', error);
            return true;
        }
    }

    showMessage(message, type) {
        const alertBox = document.getElementById('message-box');
        const alertIcon = document.getElementById('alert-icon');
        const alertMessage = document.getElementById('alert-message');

        if (!alertBox) return;

        alertMessage.textContent = message;
        alertBox.className = `alert alert-${type} alert-dismissible fade show`;
        
        const icons = {
            success: '✔️',
            danger: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        alertIcon.textContent = icons[type] || '';

        alertBox.style.display = 'block';

        setTimeout(() => {
            alertBox.classList.remove('show');
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 300);
        }, 3000);
    }

    setupTableSorting() {
        const table = document.getElementById('infoEmpleadosTable');
        if (!table) return;

        const headers = table.querySelectorAll('th.sortable');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const column = header.getAttribute('data-sort');
                const direction = header.getAttribute('data-direction') || 'asc';
                const newDirection = direction === 'asc' ? 'desc' : 'asc';

                this.sortTableByColumn(table, column, newDirection);
                this.updateSortIcons(header, newDirection, headers);
            });
        });
    }

    sortTableByColumn(table, columnName, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const headerCells = Array.from(table.querySelectorAll('thead th'));
        const columnIndex = headerCells.findIndex(th => 
            th.getAttribute('data-sort') === columnName
        );
        
        if (columnIndex === -1) return;

        rows.sort((a, b) => {
            const cellA = a.querySelector(`td[data-field="${columnName}"]`);
            const cellB = b.querySelector(`td[data-field="${columnName}"]`);
            
            if (!cellA || !cellB) return 0;
            
            const textA = this.getCellText(cellA);
            const textB = this.getCellText(cellB);

            if (!isNaN(textA) && !isNaN(textB)) {
                return direction === 'asc' ? textA - textB : textB - textA;
            }

            if (columnName.includes('fecha')) {
                const dateA = new Date(textA);
                const dateB = new Date(textB);
                if (!isNaN(dateA) && !isNaN(dateB)) {
                    return direction === 'asc' ? dateA - dateB : dateB - dateA;
                }
            }

            return direction === 'asc' 
                ? textA.localeCompare(textB) 
                : textB.localeCompare(textA);
        });

        rows.forEach(row => tbody.appendChild(row));
    }

    getCellText(cell) {
        const input = cell.querySelector('input, select');
        return input ? input.value.trim() : cell.innerText.trim();
    }

    updateSortIcons(currentHeader, direction, allHeaders) {
        allHeaders.forEach(header => {
            header.setAttribute('data-direction', 'default');
            header.querySelector('.sort-icon-default').style.display = 'inline';
            header.querySelector('.sort-icon-asc').style.display = 'none';
            header.querySelector('.sort-icon-desc').style.display = 'none';
        });
        
        currentHeader.setAttribute('data-direction', direction);
        currentHeader.querySelector('.sort-icon-default').style.display = 'none';
        currentHeader.querySelector(`.sort-icon-${direction}`).style.display = 'inline';
    }

    // Métodos globales para uso en HTML
    confirmDownload() {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            this.showMessage('No has seleccionado ningún elemento para descargar.', 'danger');
            return false;
        }

        const itemIds = Array.from(selected).map(checkbox => checkbox.value);
        document.getElementById('items_to_delete').value = itemIds.join(',');
        return true;
    }

    enableEdit() {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 0) {
            this.showMessage('Por favor, selecciona al menos un Empleado.', 'danger');
            return false;
        }
        if (selected.length > 1) {
            this.showMessage('Por favor, Selecciona un solo Empleado para editar.', 'danger');
            return false;
        }

        const row = selected[0].closest('tr');
        this.activateEditMode(row, selected[0]);
        return true;
    }

    activateEditMode(row, checkbox) {
        row.querySelectorAll('input, select').forEach(element => {
            element.setAttribute('data-original-value', element.value);
        });

        document.getElementById('select-all').disabled = true;
        document.querySelectorAll('.row-select').forEach(cb => cb.disabled = true);
        document.getElementById('edit-button').disabled = true;

        this.toggleEditElements(row, false);

        document.getElementById('save-button').classList.remove('d-none');
        document.getElementById('cancel-button').classList.remove('d-none');
    }

    toggleEditElements(row, readonly) {
        const inputs = row.querySelectorAll('input');
        const selects = row.querySelectorAll('select');
        
        inputs.forEach(input => {
            input.classList.toggle('form-control-plaintext', readonly);
            input.classList.toggle('form-control', !readonly);
            input.readOnly = readonly;
        });

        selects.forEach(select => {
            select.classList.toggle('form-control-plaintext', readonly);
            select.classList.toggle('form-control', !readonly);
            select.disabled = readonly;
        });
    }

    cancelEdit() {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length === 1) {
            const row = selected[0].closest('tr');
            this.restoreOriginalValues(row);
            this.disableEditMode(selected[0], row);
            this.showMessage('Cambios cancelados.', 'danger');
        }
    }

    restoreOriginalValues(row) {
        row.querySelectorAll('input, select').forEach(element => {
            if (element.hasAttribute('data-original-value')) {
                element.value = element.getAttribute('data-original-value');
            }
        });
    }

    disableEditMode(checkbox, row) {
        this.toggleEditElements(row, true);
        checkbox.checked = false;
        checkbox.disabled = false;

        document.getElementById('select-all').disabled = false;
        document.querySelectorAll('.row-select').forEach(cb => cb.disabled = false);
        document.getElementById('edit-button').disabled = false;

        document.getElementById('save-button').classList.add('d-none');
        document.getElementById('cancel-button').classList.add('d-none');
    }

    async saveRow() {
        const selected = document.querySelectorAll('.row-select:checked');
        if (selected.length !== 1) {
            this.showMessage('Error al guardar: No hay un Empleado seleccionado.', 'danger');
            return;
        }

        const row = selected[0].closest('tr');
        const id = selected[0].value;
        const data = this.collectRowData(row);

        try {
            const response = await fetch(`/empleado/editar/${id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                this.showMessage('Cambios guardados correctamente.', 'success');
                this.disableEditMode(selected[0], row);
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
        } catch (error) {
            console.error('Error al guardar los cambios:', error);
            this.showMessage('Error al guardar los cambios: ' + error.message, 'danger');
            this.disableEditMode(selected[0], row);
        }
    }

    collectRowData(row) {
        const data = {};
        const fields = [
            'TipoDocumento', 'Documento', 'Nombre', 'FechaNacimiento', 'FechaIngreso',
            'FechaOperacion', 'ModuloId', 'PerfilId', 'LineaId', 'CargoId', 'TituloProfesional',
            'FechaGrado', 'Universidad', 'ProfesionRealizada', 'AcademiaSAP', 'CertificadoSAP',
            'OtrasCertificaciones', 'Postgrados', 'Activo', 'FechaRetiro', 'Direccion',
            'Ciudad', 'Departamento', 'DireccionAlterna', 'Telefono1', 'Telefono2'
        ];

        fields.forEach(field => {
            const element = row.querySelector(`[name="${field}"]`);
            if (element) {
                data[field] = element.value;
            }
        });

        return data;
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    window.empleadoManager = new EmpleadoManager();
    
    // Exponer métodos globales
    window.confirmDownload = () => window.empleadoManager.confirmDownload();
    window.enableEdit = () => window.empleadoManager.enableEdit();
    window.cancelEdit = () => window.empleadoManager.cancelEdit();
    window.saveRow = () => window.empleadoManager.saveRow();
});