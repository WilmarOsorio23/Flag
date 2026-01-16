// Modulo/static/JS/Pagare.js
(() => {
  "use strict";

  const app = document.getElementById("pagare-app");
  const URLS = {
    eliminar: app?.dataset.urlEliminar || "/pagare/eliminar/",
    obtener: app?.dataset.urlObtener || "/pagares/obtener_datos/",
    actualizar: app?.dataset.urlActualizar || "/pagares/actualizar/",
    guardar: app?.dataset.urlGuardar || "/guardar_pagare/",
  };

  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const read = (sel, root = document) => (qs(sel, root)?.value ?? "").trim();

  const toFloat = (v) => {
    if (v === null || v === undefined) return 0;
    if (typeof v === "number") return Number.isFinite(v) ? v : 0;
  
    let s = String(v).trim();
    if (!s) return 0;
  
    // ✅ Caso típico input type=number o backend "1000000.00"
    if (/^-?\d+(\.\d+)?$/.test(s)) {
      const n = parseFloat(s);
      return Number.isFinite(n) ? n : 0;
    }
  
    // Limpia moneda/espacios, deja dígitos, puntos y comas
    s = s.replace(/[^\d.,-]/g, "");
  
    const dotCount = (s.match(/\./g) || []).length;
    const commaCount = (s.match(/,/g) || []).length;
  
    // Decidir separador decimal
    let decSep = null;
  
    // Si hay ambos, el último separador es el decimal
    if (dotCount && commaCount) {
      decSep = s.lastIndexOf(".") > s.lastIndexOf(",") ? "." : ",";
    } else if (dotCount) {
      // Solo puntos: si hay más de uno, son miles
      if (dotCount > 1) decSep = null;
      else {
        const [a, b] = s.split(".");
        // 1.000 (miles) -> quita punto
        if (b && b.length === 3 && a.length <= 3) decSep = null;
        else decSep = ".";
      }
    } else if (commaCount) {
      // Solo comas: si hay más de una, son miles
      if (commaCount > 1) decSep = null;
      else {
        const [a, b] = s.split(",");
        // 1,000 (miles) -> quita coma
        if (b && b.length === 3 && a.length <= 3) decSep = null;
        else decSep = ",";
      }
    }
  
    let normalized;
    if (!decSep) {
      // miles: quita puntos y comas
      normalized = s.replace(/[.,]/g, "");
    } else {
      // decimal: quita separadores de miles, y convierte decimal a "."
      const idx = s.lastIndexOf(decSep);
      const intPart = s.slice(0, idx).replace(/[.,]/g, "");
      const decPart = s.slice(idx + 1).replace(/[.,]/g, "");
      normalized = `${intPart}.${decPart}`;
    }
  
    const n = parseFloat(normalized);
    return Number.isFinite(n) ? n : 0;
  };  

  const toInt = (v) => {
    const n = parseInt(String(v ?? "").trim(), 10);
    return Number.isFinite(n) ? n : 0;
  };

  // ----------------------------
  // Mensajes
  // ----------------------------
  function notify(message, type = "info") {
    if (window.FlagMessages?.show) {
      window.FlagMessages.show(message, type);
      return;
    }

    let box = qs("#mensaje-alerta");
    if (!box) {
      box = document.createElement("div");
      box.id = "mensaje-alerta";
      box.className = "alert alert-info text-center";
      box.style.position = "fixed";
      box.style.top = "20px";
      box.style.left = "50%";
      box.style.transform = "translateX(-50%)";
      box.style.zIndex = "9999";
      box.style.minWidth = "320px";
      document.body.appendChild(box);
    }
    box.className = `alert alert-${type} text-center`;
    box.textContent = message;
    box.style.display = "block";
    setTimeout(() => (box.style.display = "none"), 3500);
  }

  function getCSRFFromMetaOrCookie() {
    const meta = qs('meta[name="csrf-token"]')?.getAttribute("content");
    if (meta) return meta;

    const hidden = qs("#csrf-token")?.value;
    if (hidden) return hidden;

    const name = "csrftoken=";
    const parts = document.cookie.split(";").map((s) => s.trim());
    for (const c of parts) {
      if (c.startsWith(name)) return decodeURIComponent(c.slice(name.length));
    }
    return qs('[name="csrfmiddlewaretoken"]')?.value || "";
  }

  function confirmUI(message) {
    return new Promise((resolve) => {
      const wrap = document.createElement("div");
      wrap.className = "pg-modal-backdrop";
      wrap.innerHTML = `
        <div class="pg-modal">
          <div class="pg-modal__body">${message}</div>
          <div class="pg-modal__actions">
            <button type="button" class="btn btn-secondary btn-sm" data-act="cancel">Cancelar</button>
            <button type="button" class="btn btn-primary btn-sm" data-act="ok">Sí</button>
          </div>
        </div>
      `;
      document.body.appendChild(wrap);

      const cleanup = () => wrap.remove();
      wrap.addEventListener("click", (e) => {
        const act = e.target?.dataset?.act;
        if (act === "ok") {
          cleanup();
          resolve(true);
        }
        if (act === "cancel") {
          cleanup();
          resolve(false);
        }
      });
    });
  }

  // ----------------------------
  // Modal: elegir pagaré activo por empleado
  // ----------------------------
  function chooseActivePagareModal(byDoc) {
    // byDoc: { [doc]: { pagares: [{id, tipo_text, fecha_creacion, estado_text, ...}] } }
    return new Promise((resolve, reject) => {
      const docs = Object.keys(byDoc).filter((d) => (byDoc[d]?.pagares?.length || 0) > 1);
      if (!docs.length) return resolve({}); // no requiere elegir

      const wrap = document.createElement("div");
      wrap.className = "pg-modal-backdrop";

      const sectionsHtml = docs
        .map((doc) => {
          const cardTitle =
            qs(`.pagare-employee-card[data-doc="${doc}"] .fw-bold`)?.textContent?.trim() || `Empleado ${doc}`;

          // preselección: el más reciente (fecha_creacion desc)
          const sorted = [...byDoc[doc].pagares].sort((a, b) =>
            String(b.fecha_creacion || "").localeCompare(String(a.fecha_creacion || ""))
          );
          const defaultId = sorted[0]?.id;

          const options = sorted
            .map((p) => {
              const label = `#${p.id} · ${p.fecha_creacion || "—"} · ${p.tipo_text || "—"} · ${p.estado_text || "—"}`;
              return `
                <label class="pg-radio">
                  <input type="radio" name="pg_active_${doc}" value="${p.id}" ${
                String(p.id) === String(defaultId) ? "checked" : ""
              }>
                  <span>${label}</span>
                </label>
              `;
            })
            .join("");

          return `
            <div class="pg-modal__section" data-doc="${doc}">
              <div class="pg-modal__section-title">${cardTitle}</div>
              <div class="pg-modal__section-sub">¿Cuál pagaré quieres editar como activo?</div>
              <div class="pg-modal__radios">${options}</div>
            </div>
          `;
        })
        .join("");

      wrap.innerHTML = `
        <div class="pg-modal pg-modal--lg">
          <div class="pg-modal__header">
            <div class="pg-modal__title">Seleccionar pagaré activo por empleado</div>
            <div class="pg-modal__subtitle">Si un empleado tiene varios pagarés cargados, elige cuál vas a editar.</div>
          </div>

          <div class="pg-modal__content">
            ${sectionsHtml}
          </div>

          <div class="pg-modal__actions">
            <button type="button" class="btn btn-outline-danger btn-sm" data-act="cancel">Cancelar</button>
            <button type="button" class="btn btn-success btn-sm" data-act="ok">
              <i class="fas fa-check me-1"></i>Continuar
            </button>
          </div>
        </div>
      `;

      document.body.appendChild(wrap);

      const cleanup = () => wrap.remove();

      wrap.addEventListener("click", (e) => {
        const act = e.target?.dataset?.act;
        if (!act) return;

        if (act === "cancel") {
          cleanup();
          reject(new Error("Selección cancelada"));
          return;
        }

        if (act === "ok") {
          const mapping = {};
          let ok = true;

          docs.forEach((doc) => {
            const selected = qs(`input[name="pg_active_${doc}"]:checked`, wrap);
            if (!selected) ok = false;
            else mapping[doc] = selected.value;
          });

          if (!ok) {
            notify("Debes seleccionar un pagaré activo para cada empleado con múltiples pagarés.", "warning");
            return;
          }

          cleanup();
          resolve(mapping);
        }
      });
    });
  }

  // ----------------------------
  // Data inicial: pagarés desde el HTML oculto
  // ----------------------------
  const pagares = qsa("#pagares-data div").map((n) => ({
    id: (n.dataset.pagareId || "").trim(),
    documento: (n.dataset.documento || "").trim(),
    tipo: (n.dataset.tipo || "").trim(),
    fecha: (n.dataset.fecha || "").trim(),
    estado: (n.dataset.estado || "").trim(),
  }));

  // UI refs
  const empleadoCheckboxes = qsa('#dropdownEmpleado + .dropdown-menu input[type="checkbox"]');
  const dropdownEmpleadoBtn = qs("#dropdownEmpleado");

  const contenedorPagares = qs("#contenedor-pagares");
  const dropdownPagaresBtn = qs("#dropdownPagares");
  const listaPagares = qs("#lista-pagares");

  const btnEliminar = qs("#btn-eliminar-pagares");
  const btnActualizar = qs("#btn-actualizar-pagares");
  const btnGuardarUpdate = qs("#guardar-pagares-btn");
  const btnCancelarUpdate = qs("#cancelar-pagares-btn");
  const pill = qs("#pagare-mode-pill");

  const offcanvasEl = qs("#offcanvasPagareSummary");

  // Estado
  let activeDoc = null;

  const state = {
    isLoading: false,
    loadedIds: [],
    // por documento
    byDoc: {
      // [doc]: { pagares: [p], planeadasByPagare: Map(pid => []), ejecutadasByPagare: Map(pid => []) }
    },
    activePagareByDoc: {
      // [doc]: pid
    },
  };

  // ----------------------------
  // UI helpers
  // ----------------------------
  function setModePill(text, loading = false) {
    if (!pill) return;
    if (loading) {
      pill.innerHTML = `<span class="pagare-loading-dot"></span>${text}`;
    } else {
      pill.textContent = text;
    }
  }

  function setLoading(v) {
    state.isLoading = !!v;
    app.dataset.isLoading = state.isLoading ? "1" : "";
    updateActionButtons();
  }

  function getSelectedPagareIds() {
    return qsa('#lista-pagares input[type="checkbox"]:checked').map((cb) => cb.value);
  }

  function isLoadedForSelection() {
    const sel = getSelectedPagareIds().join(",");
    const loaded = state.loadedIds.join(",");
    return !!sel && sel === loaded;
  }

  function setEditMode(isEdit) {
    app.dataset.isEdit = isEdit ? "1" : "";
    if (btnGuardarUpdate) btnGuardarUpdate.classList.toggle("d-none", !isEdit);
    if (btnCancelarUpdate) btnCancelarUpdate.classList.toggle("d-none", !isEdit);
    if (btnActualizar) btnActualizar.classList.toggle("d-none", isEdit);
  }

  function syncDocUI() {
    // ✅ Mostrar/ocultar “Crear pagaré” por empleado dependiendo si ese doc tiene pagarés cargados
    qsa(".pagare-employee-card[data-doc]").forEach((card) => {
      const doc = card.dataset.doc;
      const hasLoaded = !!state.byDoc[doc]?.pagares?.length;

      // Crear
      const btnCreate = qs(".btn-guardar-pagare", card);
      if (btnCreate) btnCreate.classList.toggle("d-none", hasLoaded);

      // Bloquear planeado en edición (solo si doc cargado)
      const ddPlan = qs(`#dropdownActividades_${doc}`);
      const btnAddPlan = qs(`.btn-agregar-actividades[data-documento="${doc}"]`);
      if (ddPlan) ddPlan.disabled = hasLoaded;
      if (btnAddPlan) btnAddPlan.disabled = hasLoaded;

      // Mostrar selector “Pagaré activo” en edición para ese doc
      const wrapSel = qs(`#pg-active-wrap-${doc}`);
      if (wrapSel) wrapSel.classList.toggle("d-none", !hasLoaded);
    });
  }

  function resetGlobalSummaryUI() {
    const set = (id, v) => { const el = qs(id); if (el) el.textContent = v; };
    set("#g-doc", "—");
    set("#g-ejec", "0%");
    const bar = qs("#g-bar");
    if (bar) bar.style.width = "0%";
    set("#g-valor", "$0");
    set("#g-otorgado", "$0");
    set("#g-pendiente", "$0");
    set("#g-cuota", "$0");
    set("#g-plan", "0.00");
    set("#g-ejec-h", "0.00");
    set("#g-pend-h", "0.00");
    set("#g-cond", "—");
  }
  
  function resetCardToCreate(doc) {
    const setVal = (id, val) => { const el = qs(`#${id}`); if (el) el.value = val; };
    const setDis = (id, dis) => { const el = qs(`#${id}`); if (el) el.disabled = dis; };
  
    // General
    setVal(`pagare_id_${doc}`, "");
    setVal(`fecha_creacion_${doc}`, "");
    setVal(`tipo_pagare_${doc}`, "");
    setVal(`estado_${doc}`, "proceso");
    setVal(`descripcion_${doc}`, "");
    setVal(`meses_condonacion_${doc}`, "");
    setVal(`valor_pagare_${doc}`, "");
    setVal(`ejecucion_${doc}`, "");
    setVal(`fecha_inicio_${doc}`, "");
    setVal(`fecha_fin_${doc}`, "");
    setVal(`valor_capacitacion_${doc}`, "");
    setVal(`saldo_pendiente_${doc}`, "");
    setDis(`fecha_inicio_${doc}`, true); // vuelve a estar bloqueada
  
    // Totales
    setVal(`total-planeado-${doc}`, "0.00");
    setVal(`total-ejecutado-${doc}`, "0.00");
  
    // Badge estado
    const badge = qs(`#badge-estado-${doc}`);
    if (badge) {
      badge.textContent = "Proceso";
      badge.className = "badge pagare-status-badge text-bg-primary";
    }
  
    // Selector pagaré activo (por empleado)
    const wrapSel = qs(`#pg-active-wrap-${doc}`);
    if (wrapSel) wrapSel.classList.add("d-none");
    const sel = qs(`#selector_pagare_${doc}`);
    if (sel) sel.innerHTML = `<option value="">—</option>`;
  
    // Limpia checkboxes del dropdown de actividades (por si quedaron marcados)
    const card = qs(`.pagare-employee-card[data-doc="${doc}"]`);
    if (card) {
      qsa(".actividad-checkbox", card).forEach((cb) => (cb.checked = false));
    }
  
    // Tablas planeado / ejecutado
    const tbodyPlan = qs(`#actividades-${doc}`);
    const tbodyEj = qs(`#ejecutado-${doc}`);
    if (tbodyPlan) tbodyPlan.innerHTML = "";
    if (tbodyEj) tbodyEj.innerHTML = "";
  
    ensurePlaceholder(tbodyPlan, 3);
    ensurePlaceholder(tbodyEj, 3);
  
    // Rehabilitar planeado (crear)
    const ddPlan = qs(`#dropdownActividades_${doc}`);
    const btnAddPlan = qs(`.btn-agregar-actividades[data-documento="${doc}"]`);
    if (ddPlan) ddPlan.disabled = false;
    if (btnAddPlan) btnAddPlan.disabled = false;
  }
  
  function resetAllToCreateMode({ keepEmployeeSelection = true } = {}) {
    // Desmarca pagarés seleccionados
    qsa('#lista-pagares input[type="checkbox"]').forEach((cb) => (cb.checked = false));
  
    // Limpia state
    state.loadedIds = [];
    state.byDoc = {};
    state.activePagareByDoc = {};
    activeDoc = null;
  
    // UI modo crear
    setEditMode(false);
    setModePill("Modo: Crear");
    syncDocUI(); // vuelve a mostrar botones "Crear pagaré" y habilita planeado
    updateActionButtons();
  
    // Limpia todos los cards visibles
    qsa(".pagare-employee-card[data-doc]").forEach((card) => {
      const doc = card.dataset.doc;
      resetCardToCreate(doc);
    });
  
    // Limpia resumen
    resetGlobalSummaryUI();
  
    // Si el offcanvas está abierto, lo cierra
    if (window.bootstrap?.Offcanvas && offcanvasEl) {
      const inst = window.bootstrap.Offcanvas.getInstance(offcanvasEl);
      if (inst) inst.hide();
    }
  
    // Opcional: si quieres también limpiar empleados seleccionados (normalmente NO)
    if (!keepEmployeeSelection) {
      empleadoCheckboxes.forEach((cb) => (cb.checked = false));
      updateEmpleadoLabel();
      renderPagaresDropdown();
    }
  }  

  function updateEmpleadoLabel() {
    const selected = empleadoCheckboxes
      .filter((cb) => cb.checked)
      .map((cb) => cb.closest("label")?.textContent?.trim() || cb.value);

    const base = dropdownEmpleadoBtn?.getAttribute("data-selected-text") || "Seleccione Empleados Activos";
    if (dropdownEmpleadoBtn) dropdownEmpleadoBtn.textContent = selected.length ? selected.join(", ") : base;
  }

  function getSelectedDocs() {
    return empleadoCheckboxes.filter((cb) => cb.checked).map((cb) => (cb.value || "").trim());
  }

  function updateActionButtons() {
    const selected = qsa('#lista-pagares input[type="checkbox"]:checked').length;
    const can = selected > 0 && isLoadedForSelection() && !state.isLoading;
    if (btnEliminar) btnEliminar.disabled = !can;
    if (btnActualizar) btnActualizar.disabled = !can;
  }

  function renderPagaresDropdown() {
    const docs = getSelectedDocs();
    const filtered = docs.length ? pagares.filter((p) => docs.includes(p.documento)) : pagares;

    if (listaPagares) listaPagares.innerHTML = "";

    // reset
    state.loadedIds = [];
    state.byDoc = {};
    state.activePagareByDoc = {};
    setEditMode(false);
    setModePill("Modo: Crear");
    syncDocUI();
    updateActionButtons();

    if (filtered.length === 0) {
      if (contenedorPagares) contenedorPagares.style.display = "none";
      if (dropdownPagaresBtn) dropdownPagaresBtn.disabled = true;
      if (listaPagares) listaPagares.innerHTML = '<li class="dropdown-item text-muted">No hay pagarés para este empleado</li>';
      return;
    }

    if (contenedorPagares) contenedorPagares.style.display = "block";
    if (dropdownPagaresBtn) dropdownPagaresBtn.disabled = false;

    for (const p of filtered) {
      const li = document.createElement("li");
      li.className = "dropdown-item";
      li.innerHTML = `
        <input type="checkbox" name="pagare" value="${p.id}" id="pagare_${p.id}">
        <label for="pagare_${p.id}" class="ms-2">
          ${p.tipo} | ${p.fecha} | #${p.id} | ${p.estado}
        </label>
      `;
      listaPagares.appendChild(li);
    }
    updateActionButtons();
  }

  // ----------------------------
  // Helpers tablas
  // ----------------------------
  function ensurePlaceholder(tbody, colSpan = 3) {
    if (!tbody) return;
    const hasRows = !!qs('tr[data-actividad-id]', tbody);
    const placeholder = qs("tr.no-actividades", tbody);

    if (hasRows && placeholder) placeholder.remove();

    if (!hasRows && !placeholder) {
      tbody.insertAdjacentHTML(
        "beforeend",
        `<tr class="no-actividades">
          <td colspan="${colSpan}" class="text-center py-3 bg-light">
            <i class="fas fa-info-circle"></i> No hay actividades
          </td>
        </tr>`
      );
    }
  }

  function getPlanMap(doc) {
    const map = new Map();
    qsa(`#actividades-${doc} tr[data-actividad-id]`).forEach((tr) => {
      const id = tr.dataset.actividadId;
      const horas = parseFloat(qs(".horas-planeadas", tr)?.value || "0") || 0;
      map.set(String(id), horas);
    });
    return map;
  }

  function ensureEjecutadoHasPlaneado(doc) {
    const plan = getPlanMap(doc);
    const tbodyEj = qs(`#ejecutado-${doc}`);
    if (!tbodyEj) return;

    plan.forEach((horasPlan, actId) => {
      if (!qs(`tr[data-actividad-id="${actId}"]`, tbodyEj)) {
        const nombre =
          qs(`#actividades-${doc} tr[data-actividad-id="${actId}"] td`)?.textContent?.trim() || "";

        const tr = document.createElement("tr");
        tr.className = "fila-ejecutado";
        tr.dataset.actividadId = actId;
        tr.innerHTML = `
          <td>${nombre}</td>
          <td>
            <input type="number" class="form-control horas-ejecutadas" value="0">
            <div class="ej-diff">
              Planeado: <b class="p">${horasPlan.toFixed(2)}</b> · Pendiente: <b class="d">${horasPlan.toFixed(2)}</b>
            </div>
          </td>
          <td>
            <button type="button" class="btn btn-danger btn-sm btn-remover-ejecutado">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        `;
        tbodyEj.appendChild(tr);
      }
    });

    ensurePlaceholder(tbodyEj, 3);
  }

  function updateDiffBadges(doc) {
    const plan = getPlanMap(doc);
    qsa(`#ejecutado-${doc} tr[data-actividad-id]`).forEach((tr) => {
      const id = String(tr.dataset.actividadId);
      const planH = plan.get(id) || 0;
      const ejH = parseFloat(qs(".horas-ejecutadas", tr)?.value || "0") || 0;
      const pendiente = Math.max(0, planH - ejH);

      const pEl = qs(".ej-diff .p", tr);
      const dEl = qs(".ej-diff .d", tr);
      if (pEl) pEl.textContent = planH.toFixed(2);
      if (dEl) dEl.textContent = pendiente.toFixed(2);
    });
  }

  // ----------------------------
  // Resumen
  // ----------------------------
  function setActiveDoc(doc) {
    if (!doc) return;
    activeDoc = String(doc);

    qsa(".pagare-employee-card").forEach((c) => c.classList.toggle("is-active", c.dataset.doc === activeDoc));
    const card = qs(`.pagare-employee-card[data-doc="${activeDoc}"]`);
    if (card) calcCard(card);
  }

  function updateGlobalSummary(doc, values) {
    const { pct, valorPagare, otorgado, pendienteValor, cuota, planH, ejH, pendH, condText } = values;

    const gDoc = qs("#g-doc");
    const gEjec = qs("#g-ejec");
    const gBar = qs("#g-bar");
    const gValor = qs("#g-valor");
    const gOt = qs("#g-otorgado");
    const gPend = qs("#g-pendiente");
    const gCuota = qs("#g-cuota");
    const gPlan = qs("#g-plan");
    const gEjH = qs("#g-ejec-h");
    const gPendH = qs("#g-pend-h");
    const gCond = qs("#g-cond");

    if (gDoc) gDoc.textContent = `#${doc}`;
    if (gEjec) gEjec.textContent = `${pct.toFixed(2)}%`;
    if (gBar) gBar.style.width = `${pct.toFixed(2)}%`;

    if (gValor) gValor.textContent = `${Math.round(valorPagare).toLocaleString("es-CO")}`;
    if (gOt) gOt.textContent = `${Math.round(otorgado).toLocaleString("es-CO")}`;
    if (gPend) gPend.textContent = `${Math.round(pendienteValor).toLocaleString("es-CO")}`;
    if (gCuota) gCuota.textContent = `${Math.round(cuota).toLocaleString("es-CO")}`;

    if (gPlan) gPlan.textContent = planH.toFixed(2);
    if (gEjH) gEjH.textContent = ejH.toFixed(2);
    if (gPendH) gPendH.textContent = pendH.toFixed(2);

    if (gCond) gCond.textContent = condText;
  }

  // ----------------------------
  // Cálculos por card
  // ----------------------------
  function calcCard(card) {
    const doc = card?.dataset?.doc;
    if (!doc) return;

    const tbodyPlan = qs(`#actividades-${doc}`);
    const tbodyEj = qs(`#ejecutado-${doc}`);

    ensurePlaceholder(tbodyPlan, 3);
    ensurePlaceholder(tbodyEj, 3);
    ensureEjecutadoHasPlaneado(doc);

    const totalPlaneadoInput = qs(`#total-planeado-${doc}`);
    const totalEjecutadoInput = qs(`#total-ejecutado-${doc}`);
    const ejecucionInput = qs(`#ejecucion_${doc}`);
    const valorPagareInput = qs(`#valor_pagare_${doc}`);
    const valorCapInput = qs(`#valor_capacitacion_${doc}`);
    const saldoPendInput = qs(`#saldo_pendiente_${doc}`);
    const fechaInicio = qs(`#fecha_inicio_${doc}`);
    const fechaFin = qs(`#fecha_fin_${doc}`);
    const mesesInput = qs(`#meses_condonacion_${doc}`);
    const estadoSel = qs(`#estado_${doc}`);
    const badgeEstado = qs(`#badge-estado-${doc}`);

    const horasPlaneadas = qsa(`#actividades-${doc} .horas-planeadas`).reduce(
      (sum, i) => sum + (parseFloat(i.value) || 0),
      0
    );
    const horasEjecutadas = qsa(`#ejecutado-${doc} .horas-ejecutadas`).reduce(
      (sum, i) => sum + (parseFloat(i.value) || 0),
      0
    );

    if (totalPlaneadoInput) totalPlaneadoInput.value = horasPlaneadas.toFixed(2);
    if (totalEjecutadoInput) totalEjecutadoInput.value = horasEjecutadas.toFixed(2);

    const porcentaje = horasPlaneadas > 0 ? (horasEjecutadas / horasPlaneadas) * 100 : 0;
    const pct = Math.max(0, Math.min(100, porcentaje));
    if (ejecucionInput) ejecucionInput.value = `${pct.toFixed(2)}%`;

    if (fechaInicio) {
      const can = horasPlaneadas > 0 && pct.toFixed(2) === "100.00";
      fechaInicio.disabled = !can;
      if (!can) {
        fechaInicio.value = "";
        if (fechaFin) fechaFin.value = "";
      }
    }

    const valorPagare = valorPagareInput ? toFloat(valorPagareInput.value) : 0;
    const otorgado = (valorPagare * pct) / 100;
    if (valorCapInput) valorCapInput.value = otorgado.toFixed(2);

    const pendienteValor = Math.max(0, valorPagare - otorgado);
    if (saldoPendInput) saldoPendInput.value = pendienteValor.toFixed(2);

    if (fechaInicio && fechaFin && mesesInput) {
      const meses = toInt(mesesInput.value);
      if (!fechaInicio.value || fechaInicio.disabled || !meses) {
        fechaFin.value = "";
      } else {
        const base = new Date(fechaInicio.value);
        const d = new Date(base);
        d.setMonth(d.getMonth() + meses);
        if (d.getDate() !== base.getDate()) d.setDate(0);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        fechaFin.value = `${y}-${m}-${day}`;
      }
    }

    if (estadoSel && badgeEstado) {
      const st = (estadoSel.value || "proceso").toLowerCase();
      badgeEstado.textContent = st.charAt(0).toUpperCase() + st.slice(1);
      badgeEstado.className =
        "badge pagare-status-badge " +
        (st === "terminado" ? "text-bg-success" : st === "cancelado" ? "text-bg-danger" : "text-bg-primary");
    }

    updateDiffBadges(doc);

    const meses = mesesInput ? toInt(mesesInput.value) : 0;
    const cuota = meses > 0 ? valorPagare / meses : 0;

    const pendH = Math.max(0, horasPlaneadas - horasEjecutadas);
    const condText = fechaInicio?.value && fechaFin?.value ? `${fechaInicio.value} → ${fechaFin.value}` : "—";

    if (String(activeDoc) === String(doc)) {
      updateGlobalSummary(doc, {
        pct,
        valorPagare,
        otorgado,
        pendienteValor,
        cuota,
        planH: horasPlaneadas,
        ejH: horasEjecutadas,
        pendH,
        condText,
      });
    }
  }

  function calcAll() {
    qsa(".card[data-doc]").forEach(calcCard);
  }

  // ----------------------------
  // Fetch
  // ----------------------------
  async function fetchDetails(ids) {
    const csrf = getCSRFFromMetaOrCookie();
    const res = await fetch(URLS.obtener, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ pagare_ids: ids }),
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(json?.message || json?.error || "Error al obtener datos");
    return json;
  }

  // ----------------------------
  // Construir state.byDoc desde server
  // ----------------------------
  function buildStateFromServer(data) {
    const { pagares: ps = [], planeadas = [], ejecutadas = [] } = data || {};

    const byDoc = {};

    // group pagarés
    ps.forEach((p) => {
      const doc = String(p.documento);
      byDoc[doc] ||= { pagares: [], planeadasByPagare: new Map(), ejecutadasByPagare: new Map() };

      byDoc[doc].pagares.push({
        ...p,
        id: String(p.id),
        tipo_text: p?.tipo_pagare?.nombre || p?.tipo_pagare?.desc || p?.tipo_pagare?.id || "",
        estado_text: p.estado || "",
        fecha_creacion: p.fecha_creacion || "",
      });
    });

    // group planeadas
    planeadas.forEach((it) => {
      const pid = String(it.pagare_id);
      const doc = Object.keys(byDoc).find((d) => byDoc[d].pagares.some((p) => String(p.id) === pid));
      if (!doc) return;

      const m = byDoc[doc].planeadasByPagare;
      if (!m.has(pid)) m.set(pid, []);
      m.get(pid).push(it);
    });

    // group ejecutadas
    ejecutadas.forEach((it) => {
      const pid = String(it.pagare_id);
      const doc = Object.keys(byDoc).find((d) => byDoc[d].pagares.some((p) => String(p.id) === pid));
      if (!doc) return;

      const m = byDoc[doc].ejecutadasByPagare;
      if (!m.has(pid)) m.set(pid, []);
      m.get(pid).push(it);
    });

    return byDoc;
  }

  // ----------------------------
  // Aplicar pagaré activo a un doc
  // ----------------------------
  function applyPagareToDoc(doc, pagareId) {
    const docState = state.byDoc[String(doc)];
    if (!docState) return;

    const p = docState.pagares.find((x) => String(x.id) === String(pagareId));
    if (!p) return;

    const card = qs(`.pagare-employee-card[data-doc="${doc}"]`);
    if (!card) return;

    const setVal = (id, val) => {
      const el = qs(`#${id}`);
      if (el) el.value = val ?? "";
    };

    // General
    setVal(`pagare_id_${doc}`, p.id);
    setVal(`fecha_creacion_${doc}`, p.fecha_creacion);
    setVal(`tipo_pagare_${doc}`, p?.tipo_pagare?.id ?? p?.tipo_pagare ?? "");
    setVal(`descripcion_${doc}`, p.descripcion);
    setVal(`fecha_inicio_${doc}`, p.fecha_inicio || "");
    setVal(`fecha_fin_${doc}`, p.fecha_fin || "");
    setVal(`meses_condonacion_${doc}`, p.meses_condonacion ?? 0);
    setVal(`valor_pagare_${doc}`, p.valor_pagare);
    setVal(`estado_${doc}`, (p.estado || "proceso").toLowerCase());
    setVal(`valor_capacitacion_${doc}`, (p.valor_capacitacion ?? 0).toFixed?.(2) ?? p.valor_capacitacion);

    // Planeado (bloqueado)
    const tbodyPlan = qs(`#actividades-${doc}`);
    if (tbodyPlan) {
      tbodyPlan.innerHTML = "";
      const items = docState.planeadasByPagare.get(String(p.id)) || [];
      if (!items.length) {
        ensurePlaceholder(tbodyPlan, 3);
      } else {
        items.forEach((it) => {
          const tr = document.createElement("tr");
          tr.dataset.actividadId = it.actividad_id;
          tr.innerHTML = `
            <td>${it.actividad_nombre}</td>
            <td><input type="number" class="form-control horas-planeadas" value="${it.horas_planeadas}" disabled></td>
            <td><button type="button" class="btn btn-danger btn-sm btn-remover" disabled><i class="fas fa-trash"></i></button></td>
          `;
          tbodyPlan.appendChild(tr);
        });
      }
      ensurePlaceholder(tbodyPlan, 3);
    }

    // Ejecutado (editable)
    const tbodyEj = qs(`#ejecutado-${doc}`);
    if (tbodyEj) {
      tbodyEj.innerHTML = "";
      const itemsEj = docState.ejecutadasByPagare.get(String(p.id)) || [];
      itemsEj.forEach((it) => {
        const tr = document.createElement("tr");
        tr.className = "fila-ejecutado";
        tr.dataset.actividadId = it.actividad_id;
        tr.innerHTML = `
          <td>${it.actividad_nombre}</td>
          <td>
            <input type="number" class="form-control horas-ejecutadas" value="${it.horas_ejecutadas}">
            <div class="ej-diff">
              Planeado: <b class="p">0.00</b> · Pendiente: <b class="d">0.00</b>
            </div>
          </td>
          <td><button type="button" class="btn btn-danger btn-sm btn-remover-ejecutado"><i class="fas fa-trash"></i></button></td>
        `;
        tbodyEj.appendChild(tr);
      });
      ensurePlaceholder(tbodyEj, 3);
    }

    // Heredar planeado -> ejecutado
    ensureEjecutadoHasPlaneado(doc);

    // Set selector UI
    const selector = qs(`#selector_pagare_${doc}`);
    if (selector) selector.value = String(p.id);

    state.activePagareByDoc[String(doc)] = String(p.id);

    calcCard(card);
  }

  function fillSelectorsForDocs() {
    Object.keys(state.byDoc).forEach((doc) => {
      const selector = qs(`#selector_pagare_${doc}`);
      if (!selector) return;

      const list = [...state.byDoc[doc].pagares].sort((a, b) =>
        String(b.fecha_creacion || "").localeCompare(String(a.fecha_creacion || ""))
      );

      selector.innerHTML = list
        .map((p) => {
          const label = `#${p.id} · ${p.fecha_creacion || "—"} · ${p.tipo_text || "—"} · ${p.estado_text || "—"}`;
          return `<option value="${p.id}">${label}</option>`;
        })
        .join("");

      // Si no hay activo aún, deja el más reciente por defecto
      if (!state.activePagareByDoc[doc] && list[0]) state.activePagareByDoc[doc] = String(list[0].id);
      if (state.activePagareByDoc[doc]) selector.value = String(state.activePagareByDoc[doc]);

      // change handler
      selector.onchange = () => applyPagareToDoc(doc, selector.value);
    });
  }

  // ----------------------------
  // Cargar pagarés seleccionados (y pedir activo por doc)
  // ----------------------------
  async function loadSelectedPagares() {
    const ids = getSelectedPagareIds();

    if (!ids.length) {
      state.loadedIds = [];
      state.byDoc = {};
      state.activePagareByDoc = {};
      setEditMode(false);
      setModePill("Modo: Crear");
      syncDocUI();
      updateActionButtons();
      return;
    }

    setLoading(true);
    setModePill("Cargando pagaré(s)…", true);

    try {
      const data = await fetchDetails(ids);

      state.loadedIds = ids;
      state.byDoc = buildStateFromServer(data);
      state.activePagareByDoc = {};

      // ✅ Llenar selectors por empleado
      fillSelectorsForDocs();

      // ✅ Si algún doc tiene 2+ pagarés, preguntar cuál es el activo
      const multi = Object.keys(state.byDoc).filter((doc) => (state.byDoc[doc]?.pagares?.length || 0) > 1);
      if (multi.length) {
        const mapping = await chooseActivePagareModal(state.byDoc);
        // mapping: { doc: pagareId }
        Object.entries(mapping).forEach(([doc, pid]) => (state.activePagareByDoc[doc] = pid));
      } else {
        // default: más reciente por doc
        Object.keys(state.byDoc).forEach((doc) => {
          const sorted = [...state.byDoc[doc].pagares].sort((a, b) =>
            String(b.fecha_creacion || "").localeCompare(String(a.fecha_creacion || ""))
          );
          if (sorted[0]) state.activePagareByDoc[doc] = String(sorted[0].id);
        });
      }

      // ✅ Aplicar activo por doc
      Object.keys(state.byDoc).forEach((doc) => {
        const pid = state.activePagareByDoc[doc];
        if (pid) applyPagareToDoc(doc, pid);
      });

      setEditMode(true);
      setModePill("Modo: Editar");
      syncDocUI();
      updateActionButtons();

      notify("Pagaré(s) cargado(s). Selecciona/ajusta el pagaré activo por empleado si lo necesitas.", "info");
    } catch (e) {
      state.loadedIds = [];
      state.byDoc = {};
      state.activePagareByDoc = {};
      setEditMode(false);
      setModePill("Modo: Crear");
      syncDocUI();
      updateActionButtons();
      notify(e.message || "Error cargando pagaré(s)", "danger");
      resetAllToCreateMode({ keepEmployeeSelection: true });
    } finally {
      setLoading(false);
    }
  }

  // ----------------------------
  // Guardar (crear)
  // ----------------------------
  async function saveCreateForAllCards() {
    const cards = qsa(".pagare-employee-card[data-doc]");
    if (!cards.length) {
      notify("No hay empleados cargados para crear pagaré.", "warning");
      return;
    }

    // si está en modo edición para algún doc, no crear ahí
    const anyLoaded = Object.keys(state.byDoc).length > 0;
    if (anyLoaded) {
      notify("Estás en modo edición. Quita la selección de pagarés para volver a Crear.", "warning");
      return;
    }

    const payload = [];
    let ok = true;

    cards.forEach((card) => {
      const doc = card.dataset.doc;

      const tipo = read(`#tipo_pagare_${doc}`);
      let fecha = read(`#fecha_creacion_${doc}`);
      const valor = read(`#valor_pagare_${doc}`);
      const meses = read(`#meses_condonacion_${doc}`);
      const estado = read(`#estado_${doc}`);
      const desc = read(`#descripcion_${doc}`);

      if (!fecha) {
        const el = qs(`#fecha_creacion_${doc}`);
        if (el && el.type === "date") {
          el.value = new Date().toISOString().slice(0, 10);
          fecha = el.value;
        }
      }

      const missing = [];
      if (!tipo) missing.push("Tipo pagaré");
      if (!fecha) missing.push("Fecha creación");
      if (!valor) missing.push("Valor pagaré");
      if (!meses) missing.push("Meses de condonación");
      if (!estado) missing.push("Estado");
      if (!desc) missing.push("Descripción");

      if (missing.length) {
        notify(`Faltan: ${missing.join(", ")} para ${doc}.`, "warning");
        ok = false;
        return;
      }

      const planRows = qsa(`#actividades-${doc} tr[data-actividad-id]`);
      if (!planRows.length) {
        notify(`Debe ingresar al menos 1 actividad planeada para ${doc}.`, "warning");
        ok = false;
        return;
      }

      ensureEjecutadoHasPlaneado(doc);

      const planeado = planRows.map((tr) => ({
        actividad_id: tr.dataset.actividadId,
        horas: qs(".horas-planeadas", tr)?.value || 0,
      }));

      const ejRows = qsa(`#ejecutado-${doc} tr[data-actividad-id]`);
      const ejecutado = ejRows.map((tr) => ({
        actividad_id: tr.dataset.actividadId,
        horas: qs(".horas-ejecutadas", tr)?.value || 0,
      }));

      payload.push({
        documento: doc,
        general: {
          fecha_creacion: fecha,
          tipo_pagare: tipo,
          descripcion: desc,
          fecha_inicio: qs(`#fecha_inicio_${doc}`)?.value || null,
          fecha_fin: qs(`#fecha_fin_${doc}`)?.value || null,
          meses_condonacion: meses,
          valor_pagare: valor,
          estado,
          ejecucion: qs(`#ejecucion_${doc}`)?.value || null,
        },
        planeado,
        ejecutado,
      });
    });

    if (!ok) return;

    const csrf = getCSRFFromMetaOrCookie();
    const res = await fetch(URLS.guardar, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify(payload),
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok || json.estado !== "exito") {
      notify(json?.mensaje || "Error guardando pagaré", "danger");
      return;
    }

    notify("¡Pagaré(s) creado(s) correctamente!", "success");
    setTimeout(() => window.location.reload(), 900);
  }

  // ----------------------------
  // Guardar (update)
  // ----------------------------
  async function saveUpdateSelected() {
    const selectedIds = getSelectedPagareIds();
    if (!selectedIds.length) return notify("Selecciona al menos un pagaré para guardar.", "warning");
    if (!isLoadedForSelection()) return notify("Primero debe cargarse la selección (espera a que termine).", "warning");

    const data = {};
    let valid = true;

    qsa(".pagare-employee-card[data-doc]").forEach((card) => {
      const doc = card.dataset.doc;
      const pid = state.activePagareByDoc[doc];
      if (!pid) return;

      // Solo envía el doc si ese pid está dentro de los seleccionados
      if (!selectedIds.includes(String(pid))) return;

      const desc = read(`#descripcion_${doc}`);
      if (!desc) {
        notify(`Descripción obligatoria para ${doc}.`, "warning");
        valid = false;
        return;
      }

      ensureEjecutadoHasPlaneado(doc);

      data[doc] = {
        pagare_id: pid,
        fecha_creacion: read(`#fecha_creacion_${doc}`),
        tipo_pagare: read(`#tipo_pagare_${doc}`),
        descripcion: desc,
        fecha_inicio: read(`#fecha_inicio_${doc}`) || "",
        fecha_fin: read(`#fecha_fin_${doc}`) || "",
        meses_condonacion: read(`#meses_condonacion_${doc}`),
        valor_pagare: read(`#valor_pagare_${doc}`),
        ejecucion: (read(`#ejecucion_${doc}`) || "").replace("%", ""),
        valor_capacitacion: read(`#valor_capacitacion_${doc}`),
        estado: read(`#estado_${doc}`),
        ejecutadas: qsa(`#ejecutado-${doc} tr[data-actividad-id]`).map((tr) => ({
          actividad_id: tr.dataset.actividadId,
          horas: qs(".horas-ejecutadas", tr)?.value || 0,
        })),
      };
    });

    if (!valid) return;

    const csrf = getCSRFFromMetaOrCookie();
    const res = await fetch(URLS.actualizar, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify(data),
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok) return notify(json?.message || json?.error || "Error actualizando pagarés", "danger");

    notify(json?.mensaje || "Actualización exitosa", "success");
    setTimeout(() => window.location.reload(), 900);
  }

  // ----------------------------
  // Eliminar
  // ----------------------------
  async function deleteSelected() {
    const ids = getSelectedPagareIds();
    if (!ids.length) return notify("Seleccione al menos un pagaré para eliminar.", "warning");
    if (!isLoadedForSelection()) return notify("Primero debe cargarse la selección (espera a que termine).", "warning");

    const ok = await confirmUI("¿Está seguro de eliminar los pagarés seleccionados? Esta acción no se puede deshacer.");
    if (!ok) return;

    const csrf = getCSRFFromMetaOrCookie();
    const res = await fetch(URLS.eliminar, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ ids }),
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok || json.success === false) return notify(json?.message || "Error eliminando pagarés", "danger");

    notify("Pagaré(s) eliminado(s) correctamente.", "success");
    setTimeout(() => window.location.reload(), 900);
  }

  // ----------------------------
  // Eventos
  // ----------------------------
  empleadoCheckboxes.forEach((cb) => {
    cb.addEventListener("change", () => {
      updateEmpleadoLabel();
      renderPagaresDropdown();
    });
  });

  // ✅ Seleccionar pagaré(s) => carga + pide activo por empleado
  listaPagares?.addEventListener("change", () => loadSelectedPagares());

  btnEliminar?.addEventListener("click", deleteSelected);

  btnActualizar?.addEventListener("click", async () => {
    const ids = getSelectedPagareIds();
    if (!ids.length) return notify("Selecciona al menos un pagaré.", "warning");
    await loadSelectedPagares();
  });

  btnGuardarUpdate?.addEventListener("click", (e) => {
    e.preventDefault();
    saveUpdateSelected();
  });

  btnCancelarUpdate?.addEventListener("click", (e) => {
    e.preventDefault();
    resetAllToCreateMode({ keepEmployeeSelection: true });
    notify("Cancelado. Se limpió el formulario y volviste a modo Crear.", "info");
  });
  

  document.addEventListener("click", (e) => {
    const btnSetActive = e.target.closest(".pagare-set-active");
    if (btnSetActive) {
      const doc = btnSetActive.dataset.doc;
      setActiveDoc(doc);
      if (window.bootstrap?.Offcanvas && offcanvasEl) {
        window.bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl).show();
      }
      return;
    }

    const btnCreate = e.target.closest(".btn-guardar-pagare");
    if (btnCreate) {
      e.preventDefault();
      const doc = btnCreate.dataset.doc;
      setActiveDoc(doc);
      saveCreateForAllCards();
      return;
    }

    const btnAddPlan = e.target.closest(".btn-agregar-actividades");
    if (btnAddPlan) {
      const doc = btnAddPlan.dataset.documento;
      const card = btnAddPlan.closest(".pagare-employee-card[data-doc]");
      if (!doc || !card) return;

      const checks = qsa(".actividad-checkbox:checked", card);
      const tbody = qs(`#actividades-${doc}`);
      if (!tbody) return;

      checks.forEach((cb) => {
        const id = cb.value;
        const nombre = cb.dataset.nombre || cb.closest("label")?.textContent?.trim() || "";

        if (!qs(`tr[data-actividad-id="${id}"]`, tbody)) {
          const tr = document.createElement("tr");
          tr.dataset.actividadId = id;
          tr.innerHTML = `
            <td>${nombre}</td>
            <td><input type="number" class="form-control horas-planeadas" value=""></td>
            <td><button type="button" class="btn btn-danger btn-sm btn-remover"><i class="fas fa-trash"></i></button></td>
          `;
          tbody.appendChild(tr);
        }
        cb.checked = false;
      });

      ensurePlaceholder(tbody, 3);
      ensureEjecutadoHasPlaneado(doc);
      calcCard(card);
      return;
    }

    const btnRemovePlan = e.target.closest(".btn-remover");
    if (btnRemovePlan) {
      const row = btnRemovePlan.closest("tr");
      const card = btnRemovePlan.closest(".pagare-employee-card[data-doc]");
      const doc = card?.dataset?.doc;
      const actId = row?.dataset?.actividadId;

      row?.remove();
      if (doc && actId) qs(`#ejecutado-${doc} tr[data-actividad-id="${actId}"]`)?.remove();

      ensurePlaceholder(qs(`#actividades-${doc}`), 3);
      ensurePlaceholder(qs(`#ejecutado-${doc}`), 3);
      calcCard(card);
      return;
    }

    const btnRemoveEj = e.target.closest(".btn-remover-ejecutado");
    if (btnRemoveEj) {
      const row = btnRemoveEj.closest("tr");
      const card = btnRemoveEj.closest(".pagare-employee-card[data-doc]");
      const doc = card?.dataset?.doc;
      const actId = row?.dataset?.actividadId;

      const planRow = doc && actId ? qs(`#actividades-${doc} tr[data-actividad-id="${actId}"]`) : null;
      if (planRow) {
        const input = qs(".horas-ejecutadas", row);
        if (input) input.value = "0";
      } else {
        row?.remove();
      }

      ensurePlaceholder(qs(`#ejecutado-${doc}`), 3);
      calcCard(card);
      return;
    }
  });

  document.addEventListener("focusin", (e) => {
    const card = e.target.closest?.(".pagare-employee-card[data-doc]");
    if (!card) return;
    setActiveDoc(card.dataset.doc);
  });

  document.addEventListener("input", (e) => {
    const card = e.target.closest?.(".pagare-employee-card[data-doc]");
    if (!card) return;

    if (
      e.target.classList.contains("horas-planeadas") ||
      e.target.classList.contains("horas-ejecutadas") ||
      e.target.classList.contains("valor-pagare") ||
      e.target.classList.contains("meses-condonacion") ||
      e.target.classList.contains("fecha-inicio") ||
      e.target.classList.contains("descripcion")
    ) {
      calcCard(card);
    }
  });

  // ----------------------------
  // Init
  // ----------------------------
  updateEmpleadoLabel();
  renderPagaresDropdown();
  setEditMode(false);
  setModePill("Modo: Crear");
  calcAll();
})();
