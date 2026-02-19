/**
 * Tooltip en celdas de tabla: al pasar el ratón se muestra el contenido completo.
 * Funciona con texto directo, inputs y selects.
 */
(function () {
    'use strict';

    var tooltipEl = null;
    var showTimer = null;
    var hideTimer = null;
    var HOVER_DELAY_MS = 400;
    var HIDE_DELAY_MS = 100;

    function getTooltipElement() {
        if (tooltipEl) return tooltipEl;
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'table-cell-tooltip';
        tooltipEl.setAttribute('role', 'tooltip');
        tooltipEl.setAttribute('aria-hidden', 'true');
        document.body.appendChild(tooltipEl);
        return tooltipEl;
    }

    function getCellText(cell) {
        var input = cell.querySelector('input:not([type="checkbox"]):not([type="radio"])');
        if (input) return (input.value || '').trim();

        var select = cell.querySelector('select');
        if (select) {
            var opt = select.options[select.selectedIndex];
            return opt ? (opt.textContent || opt.text || '').trim() : '';
        }

        return (cell.textContent || '').trim().replace(/\s+/g, ' ');
    }

    function showTooltip(text, cell) {
        if (!text) return;

        var tip = getTooltipElement();
        tip.textContent = text;
        tip.setAttribute('aria-hidden', 'false');

        var rect = cell.getBoundingClientRect();
        var gap = 8;
        var viewW = window.innerWidth;
        var viewH = window.innerHeight;

        /* Preferir arriba; si no hay espacio, abajo */
        var top = rect.top - gap;
        var left = Math.max(10, Math.min(rect.left, viewW - 330)); /* 330 ≈ max-width + margen */

        tip.style.top = top + 'px';
        tip.style.left = left + 'px';
        tip.style.transform = 'translateY(-100%)'; /* Colocar justo encima de la celda */

        tip.classList.add('table-cell-tooltip--visible');

        /* Si al mostrar queda fuera por arriba, mostrar debajo */
        requestAnimationFrame(function () {
            var tipRect = tip.getBoundingClientRect();
            if (tipRect.top < 10) {
                tip.style.transform = '';
                tip.style.top = (rect.bottom + gap) + 'px';
            }
        });
    }

    function hideTooltip() {
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(function () {
            hideTimer = null;
            if (tooltipEl) {
                tooltipEl.classList.remove('table-cell-tooltip--visible');
                tooltipEl.setAttribute('aria-hidden', 'true');
                tooltipEl.style.transform = '';
            }
        }, HIDE_DELAY_MS);
    }

    function cancelShow() {
        if (showTimer) {
            clearTimeout(showTimer);
            showTimer = null;
        }
    }

    function bindCell(cell) {
        if (cell.cellTooltipBound) return;
        cell.cellTooltipBound = true;

        cell.addEventListener('mouseenter', function () {
            cancelShow();
            var text = getCellText(cell);
            if (!text) return;
            showTimer = setTimeout(function () {
                showTimer = null;
                showTooltip(text, cell);
            }, HOVER_DELAY_MS);
        });

        cell.addEventListener('mouseleave', function () {
            cancelShow();
            hideTooltip();
        });
    }

    function init() {
        var tables = document.querySelectorAll('.table-responsive, .table-responsive-informes');
        tables.forEach(function (wrap) {
            var tds = wrap.querySelectorAll('.table td');
            tds.forEach(bindCell);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
