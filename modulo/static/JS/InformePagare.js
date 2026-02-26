document.addEventListener("DOMContentLoaded", function () {
    const app = document.getElementById("informe-pagares-app");
    const fechaActual = app?.dataset?.fechaActual || new Date().toISOString().slice(0, 10);
  
    // ----------------------------
    // Dropdown labels (checkbox + radio)
    // ----------------------------
    function textFromLabel(input) {
      const lbl = input.closest("label");
      if (!lbl) return input.value;
      return lbl.innerText.replace(/\s+/g, " ").trim();
    }
  
    function updateDropdownLabel(buttonId) {
      const button = document.getElementById(buttonId);
      if (!button) return;
  
      const menu = button.nextElementSibling;
      if (!menu) return;
  
      const inputs = menu.querySelectorAll("input[type='checkbox'], input[type='radio']");
      const checked = Array.from(inputs).filter((i) => i.checked);
  
      const base = button.getAttribute("data-selected-text") || "Seleccione";
  
      if (!checked.length) {
        button.textContent = base;
        return;
      }
  
      if (checked.length === 1) {
        button.textContent = textFromLabel(checked[0]);
        return;
      }
  
      button.textContent = `${checked.length} seleccionados`;
    }
  
    function attachDropdown(buttonId) {
      const button = document.getElementById(buttonId);
      if (!button) return;
  
      const menu = button.nextElementSibling;
      if (!menu) return;
  
      menu.addEventListener("change", () => updateDropdownLabel(buttonId));
      updateDropdownLabel(buttonId);
    }
  
    attachDropdown("dropdownEmpleados");
    attachDropdown("dropdownAnio");
    attachDropdown("dropdownLinea");
    attachDropdown("dropdownTipoPagare");
  
    // ----------------------------
    // Toggle detalle cuotas
    // ----------------------------
    const toggleButton = document.getElementById("toggleDetalleCuotas");
    const detalleCuotasCard = document.getElementById("detalleCuotasCard");
  
    if (toggleButton && detalleCuotasCard) {
      toggleButton.addEventListener("click", function () {
        const isHidden = detalleCuotasCard.style.display === "none";
        detalleCuotasCard.style.display = isHidden ? "block" : "none";
        toggleButton.textContent = isHidden ? "Ocultar detalle" : "Mostrar detalle";
      });
    }
  
    // ----------------------------
    // Select all
    // ----------------------------
    const selectAllCheckbox = document.getElementById("selectAll");
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener("change", function () {
        const checkboxes = document.querySelectorAll("input[name='selected_pagares']");
        checkboxes.forEach((cb) => (cb.checked = this.checked));
      });
    }
  
    // ----------------------------
    // Exportar
    // ----------------------------
    const btnExportar = document.getElementById("btnExportar");
    if (btnExportar) {
      btnExportar.addEventListener("click", function () {
        const selectedCheckboxes = document.querySelectorAll("input[name='selected_pagares']:checked");
        const selectedIds = Array.from(selectedCheckboxes).map((cb) => cb.value);
  
        const fechaInput = document.getElementById("fechaInformeInput");
        if (fechaInput) fechaInput.value = fechaActual;
  
        if (selectedIds.length > 0) {
          document.getElementById("selectedIdsInput").value = selectedIds.join(",");
          document.getElementById("exportAllInput").value = "0";
        } else {
          document.getElementById("selectedIdsInput").value = "";
          document.getElementById("exportAllInput").value = "1";
        }
  
        document.getElementById("exportForm").submit();
      });
    }
  
    // ----------------------------
    // Detalle cuotas
    // ----------------------------
    function generarCuotas(checkbox) {
      const cuerpoTabla = document.getElementById("detalleCuotasBody");
      if (!cuerpoTabla) return;
  
      cuerpoTabla.innerHTML = "";
  
      const valorPagare = Number(checkbox.dataset.valor || 0);
      const meses = parseInt(checkbox.dataset.meses || "0", 10);
      const fechaInicioStr = (checkbox.dataset.fecha || "").trim();
      const documento = checkbox.dataset.documento || "N/A";
      const nombre = checkbox.dataset.nombre || "N/A";
  
      if (!valorPagare || !meses) {
        cuerpoTabla.innerHTML =
          '<tr><td colspan="6" class="text-center text-danger">Datos inválidos para mostrar cuotas</td></tr>';
        return;
      }
  
      let fechaInicio = null;
      if (fechaInicioStr) {
        // Esperado: YYYY-MM-DD
        const parts = fechaInicioStr.split("-").map(Number);
        if (parts.length === 3 && parts.every((n) => Number.isFinite(n))) {
          fechaInicio = new Date(parts[0], parts[1] - 1, parts[2]);
        }
      }
  
      const isFechaValida = fechaInicio && !isNaN(fechaInicio.getTime());
      const valorCuota = valorPagare / meses;
  
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
  
      for (let i = 1; i <= meses; i++) {
        let fechaFormateada = "-";
        let estado = "-";
  
        if (isFechaValida) {
          const fechaCuota = new Date(fechaInicio);
          fechaCuota.setMonth(fechaInicio.getMonth() + (i - 1));
  
          const dd = String(fechaCuota.getDate()).padStart(2, "0");
          const mm = String(fechaCuota.getMonth() + 1).padStart(2, "0");
          const yy = fechaCuota.getFullYear();
  
          fechaFormateada = `${dd}/${mm}/${yy}`;
          estado = fechaCuota <= hoy ? "Pago" : "Pendiente";
        }
  
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${documento}</td>
          <td>${nombre}</td>
          <td class="text-center">${i}</td>
          <td>${fechaFormateada}</td>
          <td class="text-end">$ ${valorCuota.toLocaleString("es-CO", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
          <td class="text-center">${estado}</td>
        `;
        cuerpoTabla.appendChild(tr);
      }
  
      if (!isFechaValida) {
        cuerpoTabla.insertAdjacentHTML(
          "afterbegin",
          `<tr><td colspan="6" class="text-center text-warning">
            No hay “Inicio Condonación”, no se puede calcular el calendario real de cuotas.
          </td></tr>`
        );
      }
    }
  
    document.addEventListener("change", (e) => {
      const cb = e.target.closest?.("input[name='selected_pagares']");
      if (!cb) return;
  
      const anyChecked = document.querySelector("input[name='selected_pagares']:checked");
      if (anyChecked) generarCuotas(cb.checked ? cb : anyChecked);
      else {
        const cuerpoTabla = document.getElementById("detalleCuotasBody");
        if (cuerpoTabla) {
          cuerpoTabla.innerHTML =
            '<tr><td colspan="6" class="text-center text-muted">Seleccione un pagaré para ver el detalle de cuotas</td></tr>';
        }
      }
    });
  
    // auto selecciona el primero (si existe)
    setTimeout(() => {
      const first = document.querySelector("input[name='selected_pagares']");
      if (first) {
        first.checked = true;
        generarCuotas(first);
      }
    }, 350);
  
  });
  