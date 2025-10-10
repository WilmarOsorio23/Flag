// Sistema unificado de mensajes flotantes
document.addEventListener('DOMContentLoaded', function() {
    initializeMessageSystem();
});

function initializeMessageSystem() {
    // Función global mejorada para mostrar mensajes
    window.showMessage = function(message, type = 'info') {
        // Intentar usar el sistema de mensajes flotantes primero
        if (window.showFloatingMessage) {
            return window.showFloatingMessage(message, type);
        }
        
        // Fallback: usar alertas Bootstrap tradicionales
        showBootstrapMessage(message, type);
    };

    // Función específica para mensajes flotantes
    window.showFloatingMessage = function(message, type = 'info') {
        clearExistingMessages();
        
        const messageDiv = createMessageElement(message, type);
        const container = getMessageContainer();
        
        container.appendChild(messageDiv);
        
        // Mostrar con animación
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 100);
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            hideMessage(messageDiv);
        }, 5000);
        
        return messageDiv;
    };

    // Función para mostrar mensajes en elementos específicos de la página
    window.showInlineMessage = function(message, type = 'info', elementId = 'message-box') {
        const messageBox = document.getElementById(elementId);
        if (!messageBox) {
            console.warn(`Elemento ${elementId} no encontrado, usando mensaje flotante`);
            return window.showMessage(message, type);
        }

        const alertIcon = document.getElementById('alert-icon');
        const alertMessage = document.getElementById('alert-message');

        if (alertMessage && alertIcon) {
            // Limpiar mensajes anteriores
            messageBox.style.display = 'none';
            messageBox.className = `alert alert-${type} alert-dismissible fade`;
            
            // Configurar nuevo mensaje
            alertMessage.textContent = message;
            const icons = {
                success: '✔️',
                danger: '❌',
                warning: '⚠️',
                info: 'ℹ️'
            };
            alertIcon.textContent = icons[type] || '';
            
            // Mostrar
            messageBox.style.display = 'block';
            messageBox.classList.add('show');

            // Auto-ocultar
            setTimeout(() => {
                messageBox.classList.remove('show');
                setTimeout(() => {
                    messageBox.style.display = 'none';
                }, 300);
            }, 5000);
        } else {
            // Fallback a mensajes flotantes
            window.showMessage(message, type);
        }
    };

    // Funciones específicas
    window.showError = function(message) {
        return window.showMessage(message, 'danger');
    };
    
    window.showSuccess = function(message) {
        return window.showMessage(message, 'success');
    };
    
    window.showWarning = function(message) {
        return window.showMessage(message, 'warning');
    };
}

// Funciones auxiliares
function clearExistingMessages() {
    const existingMessages = document.querySelectorAll('.floating-alert');
    existingMessages.forEach(message => {
        if (message.parentNode) {
            message.parentNode.removeChild(message);
        }
    });
}

function createMessageElement(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} alert-dismissible fade floating-alert`;
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    return messageDiv;
}

function getMessageContainer() {
    let container = document.getElementById('message-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'message-container';
        container.className = 'message-container';
        document.body.appendChild(container);
    }
    return container;
}

function hideMessage(messageDiv) {
    messageDiv.classList.remove('show');
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 300);
}

function showBootstrapMessage(message, type) {
    // Crear mensaje Bootstrap tradicional como fallback
    const messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        messagesContainer.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    } else {
        // Último fallback: alert nativo
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

// Inicializar mensajes existentes al cargar la página
function initializeExistingMessages() {
    const messages = document.querySelectorAll('.alert:not(.floating-alert)');
    
    messages.forEach((message, index) => {
        message.classList.add('floating-alert');
        
        setTimeout(() => {
            message.style.display = 'block';
            message.classList.add('show');
        }, index * 100);
        
        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => {
                if (message.parentNode) {
                    message.remove();
                }
            }, 300);
        }, 5000);
    });
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExistingMessages);
} else {
    initializeExistingMessages();
}