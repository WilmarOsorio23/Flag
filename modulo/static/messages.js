// Sistema de mensajes unificado – carga rápida, un solo contenedor
(function () {
  "use strict";
  if (window.__flagMessageSystemInitialized) return;
  window.__flagMessageSystemInitialized = true;

  var container = null;
  var hideTimer = null;

  function getContainer() {
    if (!container) {
      container = document.getElementById("message-container");
      if (!container) {
        container = document.createElement("div");
        container.id = "message-container";
        container.className = "message-container";
        document.body.appendChild(container);
      }
    }
    return container;
  }

  function clearFloating() {
    var list = document.querySelectorAll(".floating-alert");
    for (var i = 0; i < list.length; i++) list[i].remove();
  }

  function hideEl(el) {
    if (!el) return;
    el.classList.remove("show");
    setTimeout(function () { el.remove(); }, 200);
  }

  function show(message, type) {
    type = type || "info";
    clearFloating();
    if (hideTimer) clearTimeout(hideTimer);

    var div = document.createElement("div");
    div.className = "alert alert-" + type + " alert-dismissible fade floating-alert";
    var span = document.createElement("span");
    span.textContent = message;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-close";
    btn.setAttribute("aria-label", "Cerrar");
    btn.addEventListener("click", function () { hideEl(div); });
    div.appendChild(span);
    div.appendChild(btn);
    getContainer().appendChild(div);
    div.offsetHeight;
    div.classList.add("show");
    hideTimer = setTimeout(function () { hideEl(div); hideTimer = null; }, 4500);
    return div;
  }

  function showInline(message, type, boxId) {
    boxId = boxId || "message-box";
    var box = document.getElementById(boxId);
    if (!box) return show(message, type);
    var icon = document.getElementById("alert-icon");
    var msg = document.getElementById("alert-message");
    if (!msg) return show(message, type);
    var icons = { success: "\u2714\uFE0F", danger: "\u274C", warning: "\u26A0\uFE0F", info: "\u2139\uFE0F" };
    box.className = "alert alert-" + (type || "info") + " alert-dismissible fade show";
    msg.textContent = message;
    if (icon) icon.textContent = icons[type] || "";
    box.style.display = "block";
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      box.classList.remove("show");
      setTimeout(function () { box.style.display = "none"; hideTimer = null; }, 250);
    }, 4500);
  }

  function initDjango() {
    var alerts = document.querySelectorAll(".messages .alert");
    for (var i = 0; i < alerts.length; i++) {
      var el = alerts[i];
      var type = "info";
      if (el.classList.contains("alert-success")) type = "success";
      else if (el.classList.contains("alert-danger")) type = "danger";
      else if (el.classList.contains("alert-warning")) type = "warning";
      var text = (el.textContent || "").trim();
      if (text) show(text, type);
      el.remove();
    }
  }

  window.showFloatingMessage = show;
  window.showMessage = function (message, type) { return show(message, type); };
  window.showInlineMessage = showInline;
  window.showSuccess = function (m) { return show(m, "success"); };
  window.showError = function (m) { return show(m, "danger"); };
  window.showWarning = function (m) { return show(m, "warning"); };
  window.hideMessage = function (el) { hideEl(el); };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDjango);
  } else {
    initDjango();
  }
})();
