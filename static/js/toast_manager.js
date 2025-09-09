/**
 * Toast Manager - Sistema unificado de notificaciones toast para toda la aplicación
 * Autor: Sistema PACTA
 * Fecha: 2025
 */

class ToastManager {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    /**
     * Inicializa el contenedor de toasts
     */
    init() {
        // Crear contenedor si no existe
        if (!document.querySelector('.toast-container')) {
            this.createToastContainer();
        } else {
            this.toastContainer = document.querySelector('.toast-container');
        }
    }

    /**
     * Crea el contenedor principal de toasts
     */
    createToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        this.toastContainer.style.zIndex = '1080';
        document.body.appendChild(this.toastContainer);
    }

    /**
     * Muestra un toast de éxito
     * @param {string} message - Mensaje a mostrar
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    showSuccess(message, duration = 5000) {
        this.createToast(message, 'success', duration);
    }

    /**
     * Muestra un toast de error
     * @param {string} message - Mensaje a mostrar
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    showError(message, duration = 7000) {
        this.createToast(message, 'error', duration);
    }

    /**
     * Muestra un toast de advertencia
     * @param {string} message - Mensaje a mostrar
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    showWarning(message, duration = 6000) {
        this.createToast(message, 'warning', duration);
    }

    /**
     * Muestra un toast de información
     * @param {string} message - Mensaje a mostrar
     * @param {number} duration - Duración en milisegundos (opcional)
     */
    showInfo(message, duration = 5000) {
        this.createToast(message, 'info', duration);
    }

    /**
     * Crea y muestra un toast
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo de toast (success, error, warning, info)
     * @param {number} duration - Duración en milisegundos
     */
    createToast(message, type, duration) {
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const config = this.getToastConfig(type);
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white ${config.bgClass} border-0 mb-2`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.setAttribute('data-bs-delay', duration.toString());
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center">
                    <i class="${config.icon} me-2"></i>
                    <span>${message}</span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Cerrar"></button>
            </div>
        `;

        // Agregar al contenedor
        this.toastContainer.appendChild(toast);

        // Inicializar Bootstrap Toast
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration,
            autohide: true
        });

        // Mostrar el toast
        bsToast.show();

        // Remover del DOM cuando se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });

        return bsToast;
    }

    /**
     * Obtiene la configuración visual para cada tipo de toast
     * @param {string} type - Tipo de toast
     * @returns {object} Configuración del toast
     */
    getToastConfig(type) {
        const configs = {
            success: {
                bgClass: 'bg-success',
                icon: 'fas fa-check-circle',
                title: 'Éxito'
            },
            error: {
                bgClass: 'bg-danger',
                icon: 'fas fa-exclamation-circle',
                title: 'Error'
            },
            warning: {
                bgClass: 'bg-warning',
                icon: 'fas fa-exclamation-triangle',
                title: 'Advertencia'
            },
            info: {
                bgClass: 'bg-info',
                icon: 'fas fa-info-circle',
                title: 'Información'
            }
        };

        return configs[type] || configs.info;
    }

    /**
     * Limpia todos los toasts activos
     */
    clearAll() {
        const toasts = this.toastContainer.querySelectorAll('.toast');
        toasts.forEach(toast => {
            const bsToast = bootstrap.Toast.getInstance(toast);
            if (bsToast) {
                bsToast.hide();
            }
        });
    }

    /**
     * Muestra un toast personalizado con configuración avanzada
     * @param {object} options - Opciones del toast
     */
    showCustom(options) {
        const defaults = {
            message: '',
            type: 'info',
            duration: 5000,
            title: null,
            showCloseButton: true,
            position: 'top-end'
        };

        const config = { ...defaults, ...options };
        this.createToast(config.message, config.type, config.duration);
    }
}

// Crear instancia global
window.toastManager = new ToastManager();

// Funciones de conveniencia globales para compatibilidad
window.showSuccess = function(message, duration) {
    window.toastManager.showSuccess(message, duration);
};

window.showError = function(message, duration) {
    window.toastManager.showError(message, duration);
};

window.showWarning = function(message, duration) {
    window.toastManager.showWarning(message, duration);
};

window.showInfo = function(message, duration) {
    window.toastManager.showInfo(message, duration);
};

window.showNotification = function(message, type = 'info', duration) {
    switch(type) {
        case 'success':
            window.toastManager.showSuccess(message, duration);
            break;
        case 'error':
        case 'danger':
            window.toastManager.showError(message, duration);
            break;
        case 'warning':
            window.toastManager.showWarning(message, duration);
            break;
        case 'info':
        default:
            window.toastManager.showInfo(message, duration);
            break;
    }
};

// Reemplazar alert() con toast para mejor UX (opcional)
window.showAlert = function(message, type = 'info') {
    window.showNotification(message, type);
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    if (!window.toastManager) {
        window.toastManager = new ToastManager();
    }
});

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastManager;
}