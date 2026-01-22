// Modulo/static/JS/tarifa_clientes.js
(() => {
    "use strict";
  
    const qs = (sel, root = document) => root.querySelector(sel);
    const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  
    function notify(message, type = "info") {
      // ✅ Usa el sistema unificado (messages.js)
      if (window.showInlineMessage) return window.showInlineMessage(message, type, "message-box");
      if (window.showMessage) return window.showMessage(message, type);
      alert(`${type.toUpperCase()}: ${message}`);
    }
  
    function getCsrfToken() {
      // Meta en base.html
      const meta = qs('meta[name="csrf-token"]');
      if (meta?.content) return meta.content;
      // Fallback
      const input = qs('[name=csrfmiddlewaretoken]');
      return input?.value || "";
    }
  
    function setDisabled(el, disabled) {
      if (!el) return;
      if (el.tagName === "A") {
        el.classList.toggle("disabled", disabled);
        el.setAttribute("aria-disabled", disabled ? "true" : "false");
      } else {
        el.disabled = disabled;
      }
    }
  
    function getSelectedCheckboxes() {
      return qsa(".row-select:checked");
    }
  
    function ensureSelectOptions(selectEl, templateId) {
      if (!selectEl) return;
      if (selectEl.options.length > 0) return;
  
      const tpl = qs(`#${templateId}`);
      if (!tpl) return;
  
      selectEl.innerHTML = tpl.innerHTML;
    }
  
    // ✅ Limpia $ , . (miles) y normaliza decimales
    function normalizeNumber(value) {
      let v = String(value ?? "").trim();
  
      // quita símbolos comunes y espacios
      v = v.replace(/\s/g, "").replace(/[$€£]/g, "");
  
      const lastComma = v.lastIndexOf(",");
      const lastDot = v.lastIndexOf(".");
  
      if (lastComma !== -1 && lastDot !== -1) {
        // si la coma está después del punto => coma decimal
        if (lastComma > lastDot) {
          v = v.replace(/\./g, "").replace(",", ".");
        } else {
          // punto decimal, coma miles
          v = v.replace(/,/g, "");
        }
      } else if (lastComma !== -1) {
        const commas = (v.match(/,/g) || []).length;
        if (commas > 1) v = v.replace(/,/g, "");
        else v = v.replace(",", ".");
      } else if (lastDot !== -1) {
        const dots = (v.match(/\./g) || []).length;
        if (dots > 1) v = v.replace(/\./g, "");
      }
  
      // deja solo dígitos, punto, menos
      v = v.replace(/[^\d.-]/g, "");
      return v;
    }
  
    document.addEventListener("DOMContentLoaded", () => {
      const csrfToken = getCsrfToken();
  
      const downloadForm = qs("#download-form");
      const deleteForm = qs("#delete-form");
      const deleteBtn = qs("#delete-button");
      const selectAll = qs("#select-all");
  
      const editBtn = qs("#edit-button");
      const saveBtn = qs("#save-button");
      const cancelBtn = qs("#cancel-button");
  
      const confirmDeleteModalEl = qs("#confirmDeleteModal");
      const confirmDeleteBtn = qs("#confirm-delete-btn");
      const confirmDeleteModal = confirmDeleteModalEl ? new bootstrap.Modal(confirmDeleteModalEl) : null;
  
      // ---------- DESCARGA ----------
      if (downloadForm) {
        downloadForm.addEventListener("submit", (event) => {
          qsa(".download-hidden", downloadForm).forEach((n) => n.remove());
  
          const selected = getSelectedCheckboxes();
          if (selected.length === 0) {
            notify("No has seleccionado ningún elemento para descargar.", "danger");
            event.preventDefault();
            return;
          }
  
          selected.forEach((cb) => {
            const hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.name = cb.name; // items_to_delete
            hidden.value = cb.value;
            hidden.className = "download-hidden";
            downloadForm.appendChild(hidden);
          });
        });
      }
  
      // ---------- SELECT ALL ----------
      if (selectAll) {
        selectAll.addEventListener("change", (e) => {
          const checked = e.target.checked;
          qsa(".row-select").forEach((cb) => (cb.checked = checked));
        });
      }
  
      // ---------- PREVENIR ENTER EN FORM ----------
      qsa("form").forEach((form) => {
        form.addEventListener("keydown", (event) => {
          if (event.key === "Enter") event.preventDefault();
        });
      });
  
      // ---------- ELIMINAR ----------
      if (deleteBtn && deleteForm && confirmDeleteModal) {
        deleteBtn.addEventListener("click", (event) => {
          event.preventDefault();
          const selected = getSelectedCheckboxes();
          if (selected.length === 0) {
            notify("No has seleccionado ningún elemento para eliminar.", "danger");
            return;
          }
          confirmDeleteModal.show();
        });
  
        if (confirmDeleteBtn) {
          confirmDeleteBtn.addEventListener("click", () => {
            deleteForm.submit();
          });
        }
      }
  
      // ---------- EDICIÓN INLINE ----------
      window.enableEdit = function () {
        const selected = getSelectedCheckboxes();
        if (selected.length === 0) return notify("No has seleccionado ningún registro para editar.", "warning");
        if (selected.length > 1) return notify("Solo puedes editar un registro a la vez.", "warning");
  
        const row = selected[0].closest("tr");
        if (!row) return;
  
        const editableFields = [
          { name: "referencia", type: "select", tpl: "tpl-referencia" },
          { name: "centroCostos", type: "select", tpl: "tpl-centroCostos" },
          { name: "sitioTrabajo", type: "text" },
          { name: "valorHora", type: "text" },
          { name: "valorDia", type: "text" },
          { name: "valorMes", type: "text" },
          { name: "bolsaMes", type: "text" },
          { name: "valorBolsa", type: "text" },
          { name: "iva", type: "text" },
          { name: "moneda", type: "select", tpl: "tpl-moneda" },
        ];
  
        // Guardar originales
        editableFields.forEach((f) => {
          const el = qs(`[name="${f.name}"]`, row);
          const display = qs(`[data-display="${f.name}"]`, row);
  
          if (el) el.dataset.originalValue = el.value || el.dataset.selected || "";
          if (display) display.dataset.originalText = display.textContent.trim();
        });
  
        // Activar inputs/selects y ocultar spans
        editableFields.forEach((f) => {
          const el = qs(`[name="${f.name}"]`, row);
          const display = qs(`[data-display="${f.name}"]`, row);
  
          if (f.type === "select" && el) {
            ensureSelectOptions(el, f.tpl);
            el.value = el.dataset.selected || el.dataset.originalValue || el.value;
            el.disabled = false;
            el.classList.remove("d-none");
            el.classList.add("form-control");
          }
  
          if (f.type === "text" && el) {
            el.classList.remove("d-none");
            el.classList.add("form-control");
            el.readOnly = false;
          }
  
          if (display) display.classList.add("d-none");
        });
  
        // Bloquear checks y botones
        setDisabled(selectAll, true);
        qsa(".row-select").forEach((cb) => (cb.disabled = true));
        setDisabled(editBtn, true);
  
        saveBtn?.classList.remove("d-none");
        cancelBtn?.classList.remove("d-none");
      };
  
      window.cancelEdit = function () {
        const selected = getSelectedCheckboxes();
        if (selected.length !== 1) return;
  
        const row = selected[0].closest("tr");
        if (!row) return;
  
        const names = ["referencia", "centroCostos", "sitioTrabajo", "valorHora", "valorDia", "valorMes", "bolsaMes", "valorBolsa", "iva", "moneda"];
  
        names.forEach((name) => {
          const el = qs(`[name="${name}"]`, row);
          const display = qs(`[data-display="${name}"]`, row);
  
          if (el) {
            const original = el.dataset.originalValue ?? el.dataset.selected ?? "";
            el.value = original;
  
            if (el.tagName === "SELECT") {
              el.disabled = true;
              el.classList.add("d-none");
            } else {
              el.readOnly = true;
              el.classList.add("d-none");
              el.classList.add("form-control");
            }
          }
  
          if (display) {
            display.textContent = display.dataset.originalText || display.textContent;
            display.classList.remove("d-none");
          }
        });
  
        // Restaurar checks/botones
        setDisabled(selectAll, false);
        qsa(".row-select").forEach((cb) => (cb.disabled = false));
        setDisabled(editBtn, false);
  
        saveBtn?.classList.add("d-none");
        cancelBtn?.classList.add("d-none");
      };
  
      window.saveRow = function () {
        const selected = getSelectedCheckboxes();
        if (selected.length !== 1) {
          notify("Error al guardar: No hay un registro seleccionado.", "danger");
          return;
        }
  
        const row = selected[0].closest("tr");
        if (!row) return;
  
        const data = {
          referencia: qs('select[name="referencia"]', row)?.value?.trim() || "",
          centroCostos: qs('select[name="centroCostos"]', row)?.value?.trim() || "",
          sitioTrabajo: qs('input[name="sitioTrabajo"]', row)?.value?.trim() || "",
  
          valorHora: normalizeNumber(qs('input[name="valorHora"]', row)?.value),
          valorDia: normalizeNumber(qs('input[name="valorDia"]', row)?.value),
          valorMes: normalizeNumber(qs('input[name="valorMes"]', row)?.value),
          bolsaMes: normalizeNumber(qs('input[name="bolsaMes"]', row)?.value),
          valorBolsa: normalizeNumber(qs('input[name="valorBolsa"]', row)?.value),
  
          iva: normalizeNumber(qs('input[name="iva"]', row)?.value),
          moneda: qs('select[name="moneda"]', row)?.value?.trim() || "",
        };
  
        // ✅ No rompas con "0"
        for (const [k, v] of Object.entries(data)) {
          if (v === "" || v === null || v === undefined) {
            return notify(`El campo ${k} es obligatorio.`, "danger");
          }
        }
  
        const id = selected[0].value;
        const url = row.dataset.editUrl || `/tarifa_clientes/editar/${id}/`;
  
        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: JSON.stringify(data),
        })
          .then(async (res) => {
            if (!res.ok) {
              const txt = await res.text();
              throw new Error(`HTTP ${res.status}: ${txt.slice(0, 300)}`);
            }
            return res.json();
          })
          .then((payload) => {
            if (payload.status === "success") {
              notify("Cambios guardados correctamente.", "success");
              window.location.reload();
            } else {
              notify(`Error al guardar: ${payload.error || "Error desconocido"}`, "danger");
            }
          })
          .catch((err) => {
            console.error(err);
            notify(`Error al guardar los cambios: ${err.message}`, "danger");
          });
      };
  
      // ---------- SORTING ----------
      const table = qs("#tarifa-table");
      if (table) {
        const headers = qsa("th.sortable", table);
        const collator = new Intl.Collator("es", { numeric: true, sensitivity: "base" });
  
        headers.forEach((header) => {
          header.addEventListener("click", () => {
            const column = header.getAttribute("data-sort");
            const direction = header.getAttribute("data-direction") || "asc";
            const newDirection = direction === "asc" ? "desc" : "asc";
  
            sortTableByColumn(table, column, newDirection, collator);
  
            headers.forEach((h) => {
              h.setAttribute("data-direction", "default");
              qs(".sort-icon-default", h).style.display = "inline";
              qs(".sort-icon-asc", h).style.display = "none";
              qs(".sort-icon-desc", h).style.display = "none";
            });
  
            header.setAttribute("data-direction", newDirection);
            qs(".sort-icon-default", header).style.display = "none";
            qs(`.sort-icon-${newDirection}`, header).style.display = "inline";
          });
        });
      }
  
      function sortTableByColumn(table, columnName, direction, collator) {
        const tbody = qs("tbody", table);
        const rows = qsa("tr", tbody);
  
        const withKeys = rows.map((row) => {
          const cell = qs(`[data-field="${columnName}"]`, row);
          let key = "";
  
          if (cell) {
            const input = qs("input:not(.d-none)", cell);
            const select = qs("select:not(.d-none)", cell);
            const span = qs("span", cell);
  
            if (input) key = input.value.trim();
            else if (select) key = (select.options[select.selectedIndex]?.text || "").trim();
            else if (span) key = span.textContent.trim();
          }
  
          return { row, key };
        });
  
        withKeys.sort((a, b) => {
          const cmp = collator.compare(a.key, b.key);
          return direction === "asc" ? cmp : -cmp;
        });
  
        const frag = document.createDocumentFragment();
        withKeys.forEach(({ row }) => frag.appendChild(row));
        tbody.appendChild(frag);
      }
    });
  })();
  