/**
 * Ordenación global para tablas .table-app
 * Ciclo: normal (default) → ascendente → descendente → normal
 */
(function () {
    'use strict';

    const SORT_ICON_HTML = '<span class="sort-icon">' +
        '<i class="fas fa-sort sort-icon-default"></i>' +
        '<i class="fas fa-sort-up sort-icon-asc"></i>' +
        '<i class="fas fa-sort-down sort-icon-desc"></i>' +
        '</span>';

    function getCellText(td) {
        if (!td) return '';
        const input = td.querySelector('input, select');
        if (input) return (input.value || '').trim();
        return (td.innerText || td.textContent || '').trim();
    }

    function getCellByIndex(row, colIndex) {
        const cells = row.querySelectorAll('td');
        return cells[colIndex] || null;
    }

    function compareValues(a, b, direction, sortKey) {
        const isNumA = !isNaN(parseFloat(a)) && isFinite(a);
        const isNumB = !isNaN(parseFloat(b)) && isFinite(b);
        if (isNumA && isNumB) {
            const diff = parseFloat(a) - parseFloat(b);
            return direction === 'asc' ? diff : -diff;
        }
        const isDate = /fecha|date|f\.?\s*(inicio|fin|ingreso|retiro)|inicio|fin/i.test(String(sortKey));
        if (isDate) {
            const dA = new Date(a);
            const dB = new Date(b);
            if (!isNaN(dA.getTime()) && !isNaN(dB.getTime())) {
                const diff = dA - dB;
                return direction === 'asc' ? diff : -diff;
            }
        }
        const cmp = (a || '').localeCompare(b || '', undefined, { numeric: true });
        return direction === 'asc' ? cmp : -cmp;
    }

    function setHeaderDirection(header, direction) {
        header.setAttribute('data-direction', direction);
        const def = header.querySelector('.sort-icon-default');
        const asc = header.querySelector('.sort-icon-asc');
        const desc = header.querySelector('.sort-icon-desc');
        if (def) def.style.display = direction === 'default' ? 'inline' : 'none';
        if (asc) asc.style.display = direction === 'asc' ? 'inline' : 'none';
        if (desc) desc.style.display = direction === 'desc' ? 'inline' : 'none';
    }

    function resetOtherHeaders(headers, exceptHeader) {
        headers.forEach(function (h) {
            if (h !== exceptHeader) {
                setHeaderDirection(h, 'default');
            }
        });
    }

    function initTable(table) {
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');
        if (!thead || !tbody) return;

        const firstRow = thead.querySelector('tr');
        if (!firstRow) return;

        const headers = Array.from(firstRow.querySelectorAll('th'));
        headers.forEach(function (th, colIndex) {
            const isCheckboxOnly = th.querySelector('input[type="checkbox"]') && !th.textContent.trim().replace(/\s/g, '');
            if (isCheckboxOnly) return;

            if (!th.classList.contains('sortable')) {
                th.classList.add('sortable');
                if (!th.getAttribute('data-sort')) th.setAttribute('data-sort', String(colIndex));
                th.setAttribute('data-direction', 'default');
                if (!th.querySelector('.sort-icon')) {
                    th.insertAdjacentHTML('beforeend', SORT_ICON_HTML);
                }
            }
        });

        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.forEach(function (tr, i) {
            tr.setAttribute('data-original-order', String(i));
        });

        const sortableHeaders = firstRow.querySelectorAll('th.sortable');
        sortableHeaders.forEach(function (header) {
            header.addEventListener('click', function (ev) {
                ev.preventDefault();
                ev.stopImmediatePropagation();
                const direction = header.getAttribute('data-direction') || 'default';
                const nextDirection = direction === 'default' ? 'asc' : direction === 'asc' ? 'desc' : 'default';
                const sortKey = header.getAttribute('data-sort');
                const colIndex = headers.indexOf(header);
                if (colIndex === -1) return;

                resetOtherHeaders(Array.from(sortableHeaders), header);
                setHeaderDirection(header, nextDirection);

                const allRows = Array.from(tbody.querySelectorAll('tr'));
                if (nextDirection === 'default') {
                    allRows.sort(function (ra, rb) {
                        const oa = parseInt(ra.getAttribute('data-original-order'), 10) || 0;
                        const ob = parseInt(rb.getAttribute('data-original-order'), 10) || 0;
                        return oa - ob;
                    });
                } else {
                    allRows.sort(function (a, b) {
                        const cellA = getCellByIndex(a, colIndex);
                        const cellB = getCellByIndex(b, colIndex);
                        const textA = getCellText(cellA);
                        const textB = getCellText(cellB);
                        return compareValues(textA, textB, nextDirection, sortKey);
                    });
                }
                allRows.forEach(function (row) {
                    tbody.appendChild(row);
                });
            });
        });
    }

    function fitInputToContent(input) {
        var len = (input.value || '').length;
        if (len > 0) {
            input.setAttribute('size', len + 2);
        }
    }

    function fitSelectToContent(select) {
        var opt = select.options[select.selectedIndex];
        var text = opt ? opt.text.trim() : '';
        var ch = text.length + 2;
        select.style.minWidth = (ch < 8 ? 8 : ch) + 'ch';
    }

    function run() {
        var tables = document.querySelectorAll('table.table-app:not(.table-registro-tiempos)');
        tables.forEach(initTable);

        var tableRoots = document.querySelectorAll('table.table-app, table.table-primary');
        tableRoots.forEach(function (table) {
            table.querySelectorAll('tbody td input[type="text"], tbody td input.form-control-plaintext').forEach(function (input) {
                fitInputToContent(input);
            });
            table.querySelectorAll('tbody td select').forEach(function (select) {
                fitSelectToContent(select);
                select.addEventListener('change', function () {
                    fitSelectToContent(select);
                });
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
