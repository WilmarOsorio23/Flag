// Modulo/static/messages.js
(() => {
    "use strict";
  
    if (window.__flagMessageSystemInitialized) return;
    window.__flagMessageSystemInitialized = true;
  
    function getMessageContainer() {
      let container = document.getElementById("message-container");
      if (!container) {
        container = document.createElement("div");
        container.id = "message-container";
        container.className = "message-container";
        document.body.appendChild(container);
      }
      return container;
    }
  
    function clearExistingFloating() {
      document.querySelectorAll(".floating-alert").forEach((n) => n.remove());
    }
  
    function hideMessageElement(messageDiv) {
      if (!messageDiv) return;
      messageDiv.classList.remove("show");
      setTimeout(() => messageDiv.remove(), 250);
    }
  
    function createMessageElement(message, type) {
      const div = document.createElement("div");
      div.className = `alert alert-${type} alert-dismissible fade floating-alert`;
  
      const text = document.createElement("span");
      text.textContent = message;
  
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn-close";
      btn.setAttribute("aria-label", "Close");
      btn.addEventListener("click", () => hideMessageElement(div));
  
      div.appendChild(text);
      div.appendChild(btn);
  
      return div;
    }
  
    function showFloatingMessage(message, type = "info") {
      clearExistingFloating();
  
      const container = getMessageContainer();
      const messageDiv = createMessageElement(message, type);
      container.appendChild(messageDiv);
  
      requestAnimationFrame(() => messageDiv.classList.add("show"));
  
      setTimeout(() => hideMessageElement(messageDiv), 5000);
      return messageDiv;
    }
  
    function showBootstrapFallback(message, type) {
      const messagesContainer = document.querySelector(".messages");
      if (messagesContainer) {
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.textContent = message;
        messagesContainer.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
      } else {
        alert(`${type.toUpperCase()}: ${message}`);
      }
    }
  
    function initExistingDjangoMessages() {
      const alerts = document.querySelectorAll(".messages .alert");
      if (!alerts.length) return;
  
      alerts.forEach((el, idx) => {
        const classList = Array.from(el.classList);
        const typeClass = classList.find((c) => c.startsWith("alert-")) || "alert-info";
        const type = typeClass.replace("alert-", "") || "info";
        const text = (el.textContent || "").trim();
  
        // Mostrar escalonado
        setTimeout(() => showFloatingMessage(text, type), idx * 120);
  
        // Remover del DOM para no duplicar
        el.remove();
      });
    }
  
    function initializeMessageSystem() {
      window.showFloatingMessage = showFloatingMessage;
  
      window.showMessage = function (message, type = "info") {
        if (window.showFloatingMessage) return window.showFloatingMessage(message, type);
        return showBootstrapFallback(message, type);
      };
  
      window.hideMessage = function (messageDiv) {
        hideMessageElement(messageDiv);
      };
  
      window.showInlineMessage = function (message, type = "info", elementId = "message-box") {
        const box = document.getElementById(elementId);
        if (!box) return window.showMessage(message, type);
  
        const iconEl = document.getElementById("alert-icon");
        const msgEl = document.getElementById("alert-message");
  
        if (!iconEl || !msgEl) return window.showMessage(message, type);
  
        const icons = { success: "✔️", danger: "❌", warning: "⚠️", info: "ℹ️" };
  
        box.style.display = "none";
        box.className = `alert alert-${type} alert-dismissible fade`;
        msgEl.textContent = message;
        iconEl.textContent = icons[type] || "";
  
        box.style.display = "block";
        requestAnimationFrame(() => box.classList.add("show"));
  
        setTimeout(() => {
          box.classList.remove("show");
          setTimeout(() => (box.style.display = "none"), 250);
        }, 5000);
      };
  
      window.showError = (m) => window.showMessage(m, "danger");
      window.showSuccess = (m) => window.showMessage(m, "success");
      window.showWarning = (m) => window.showMessage(m, "warning");
  
      initExistingDjangoMessages();
    }
  
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", initializeMessageSystem);
    } else {
      initializeMessageSystem();
    }
  })();
  