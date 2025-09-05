// Sistema de mensajes flotantes mejorado
document.addEventListener('DOMContentLoaded', function() {
    // Función para mostrar mensajes flotantes
    function showFloatingMessages() {
        const messages = document.querySelectorAll('.alert:not(.floating-alert)');
        
        messages.forEach((message, index) => {
            // Agregar clase para animación
            message.classList.add('floating-alert');
            
            // Configurar timeout para mostrar
            setTimeout(() => {
                message.style.display = 'block';
                message.classList.add('show');
            }, index * 100);
            
            // Auto-ocultar después de 5 segundos
            setTimeout(() => {
                message.classList.remove('show');
                setTimeout(() => {
                    message.remove();
                }, 300);
            }, 5000);
        });
    }
    
    // Función para limpiar mensajes existentes
    function clearMessages() {
        const existingMessages = document.querySelectorAll('.floating-alert');
        existingMessages.forEach(message => message.remove());
    }
    
    // Mostrar mensajes al cargar la página
    showFloatingMessages();
    
    // Interceptar envíos de formularios para mostrar mensajes inmediatamente
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Limpiar mensajes existentes
            clearMessages();
        });
    });
    
    // Función global para mostrar mensajes personalizados
    window.showMessage = function(message, type = 'info') {
        clearMessages();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} alert-dismissible fade show floating-alert`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insertar al inicio del contenido
        const content = document.querySelector('.content-principal .container-fluid .row .col-12');
        if (content) {
            content.insertBefore(messageDiv, content.firstChild);
        }
        
        // Mostrar con animación
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 100);
        
        // Auto-ocultar
        setTimeout(() => {
            messageDiv.classList.remove('show');
            setTimeout(() => {
                messageDiv.remove();
            }, 300);
        }, 5000);
    };
    
    // Función para mostrar mensajes de error inmediatamente
    window.showError = function(message) {
        window.showMessage(message, 'danger');
    };
    
    // Función para mostrar mensajes de éxito inmediatamente
    window.showSuccess = function(message) {
        window.showMessage(message, 'success');
    };
    
    // Función para mostrar mensajes de advertencia inmediatamente
    window.showWarning = function(message) {
        window.showMessage(message, 'warning');
    };
});

// CSS para animaciones de mensajes flotantes
const style = document.createElement('style');
style.textContent = `
    .floating-alert {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        transform: translateX(100%);
        transition: transform 0.3s ease-in-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .floating-alert.show {
        transform: translateX(0);
    }
    
    .floating-alert .btn-close {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    
    @media (max-width: 768px) {
        .floating-alert {
            top: 10px;
            right: 10px;
            left: 10px;
            min-width: auto;
            max-width: none;
        }
    }
`;
document.head.appendChild(style);