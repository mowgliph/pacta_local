// Funciones para el sistema de notificaciones

class NotificationManager {
    constructor() {
        this.notificationCount = 0;
        this.notifications = [];
        this.isModalOpen = false;
        this.pollInterval = null;
        this.init();
    }

    init() {
        // Inicializar eventos
        this.bindEvents();
        // Cargar notificaciones iniciales
        this.loadNotifications();
        // Iniciar polling cada 30 segundos
        this.startPolling();
    }

    bindEvents() {
        // Evento para abrir modal de notificaciones
        const bellButton = document.getElementById('notifications-bell');
        if (bellButton) {
            bellButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleNotificationsModal();
            });
        }

        // Cerrar modal al hacer clic fuera
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('notifications-modal');
            const bellButton = document.getElementById('notifications-bell');
            
            if (modal && this.isModalOpen && 
                !modal.contains(e.target) && 
                !bellButton.contains(e.target)) {
                this.closeNotificationsModal();
            }
        });

        // Evento para marcar todas como leídas
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('mark-all-read-btn')) {
                e.preventDefault();
                this.markAllAsRead();
            }
        });

        // Evento para marcar notificación individual como leída
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('mark-read-btn')) {
                e.preventDefault();
                const notificationId = e.target.dataset.notificationId;
                this.markAsRead(notificationId);
            }
        });
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            
            if (data.success) {
                this.notifications = data.notifications;
                this.updateNotificationCount();
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Error al cargar notificaciones:', error);
        }
    }

    async updateNotificationCount() {
        try {
            const response = await fetch('/api/notifications/count');
            const data = await response.json();
            
            if (data.success) {
                this.notificationCount = data.count;
                this.updateBadge();
            }
        } catch (error) {
            console.error('Error al actualizar contador:', error);
        }
    }

    updateBadge() {
        const badge = document.getElementById('notification-count');
        if (badge) {
            if (this.notificationCount > 0) {
                badge.textContent = this.notificationCount > 99 ? '99+' : this.notificationCount;
                badge.style.display = 'block';
                badge.classList.add('pulse');
            } else {
                badge.style.display = 'none';
                badge.classList.remove('pulse');
            }
        }
    }

    toggleNotificationsModal() {
        if (this.isModalOpen) {
            this.closeNotificationsModal();
        } else {
            this.openNotificationsModal();
        }
    }

    openNotificationsModal() {
        const modal = document.getElementById('notifications-modal');
        if (modal) {
            modal.style.display = 'block';
            this.isModalOpen = true;
            // Recargar notificaciones al abrir
            this.loadNotifications();
        }
    }

    closeNotificationsModal() {
        const modal = document.getElementById('notifications-modal');
        if (modal) {
            modal.style.display = 'none';
            this.isModalOpen = false;
        }
    }

    renderNotifications() {
        const container = document.getElementById('notifications-list');
        if (!container) return;

        if (this.notifications.length === 0) {
            container.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>No tienes notificaciones</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.notifications.map(notification => {
            const timeAgo = this.getTimeAgo(notification.created_at);
            const typeIcon = this.getTypeIcon(notification.type);
            const readClass = notification.is_read ? 'read' : 'unread';

            return `
                <div class="notification-item ${readClass}" data-id="${notification.id}">
                    <div class="notification-icon ${notification.type}">
                        <i class="${typeIcon}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-header">
                            <h4 class="notification-title">${notification.title}</h4>
                            <span class="notification-time">${timeAgo}</span>
                        </div>
                        <p class="notification-message">${notification.message}</p>
                        ${!notification.is_read ? `
                            <div class="notification-actions">
                                <button class="mark-read-btn" data-notification-id="${notification.id}">
                                    <i class="fas fa-check"></i> Marcar como leída
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    getTypeIcon(type) {
        const icons = {
            'system': 'fas fa-cog',
            'contract_expiring': 'fas fa-exclamation-triangle',
            'contract_expired': 'fas fa-times-circle',
            'reminder': 'fas fa-bell',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || 'fas fa-bell';
    }

    getTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Hace unos segundos';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
        } else if (diffInSeconds < 2592000) {
            const days = Math.floor(diffInSeconds / 86400);
            return `Hace ${days} día${days > 1 ? 's' : ''}`;
        } else {
            return date.toLocaleDateString('es-ES');
        }
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            if (data.success) {
                // Actualizar la notificación en el array local
                const notification = this.notifications.find(n => n.id == notificationId);
                if (notification) {
                    notification.is_read = true;
                }
                // Recargar notificaciones y actualizar contador
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Error al marcar notificación como leída:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            if (data.success) {
                // Marcar todas las notificaciones como leídas localmente
                this.notifications.forEach(notification => {
                    notification.is_read = true;
                });
                // Recargar notificaciones y actualizar contador
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Error al marcar todas las notificaciones como leídas:', error);
        }
    }

    startPolling() {
        // Polling cada 30 segundos
        this.pollInterval = setInterval(() => {
            this.updateNotificationCount();
        }, 30000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async createSystemNotification(title, message, type = 'system') {
        try {
            const response = await fetch('/api/notifications/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    message: message,
                    type: type
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.loadNotifications();
                return true;
            }
        } catch (error) {
            console.error('Error al crear notificación del sistema:', error);
        }
        return false;
    }

    async checkContractReminders() {
        try {
            const response = await fetch('/api/notifications/check-contracts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            if (data.success) {
                this.loadNotifications();
                return data.reminders_created || 0;
            }
        } catch (error) {
            console.error('Error al verificar recordatorios de contratos:', error);
        }
        return 0;
    }
}

// Funciones legacy para compatibilidad con código existente
function openNotificationsModal() {
    if (window.notificationManager) {
        window.notificationManager.openNotificationsModal();
    }
}

function loadNotifications() {
    if (window.notificationManager) {
        window.notificationManager.loadNotifications();
    }
}

function displayNotifications(notifications) {
    if (window.notificationManager) {
        window.notificationManager.notifications = notifications;
        window.notificationManager.renderNotifications();
    }
}

function getNotificationIcon(type) {
    if (window.notificationManager) {
        return window.notificationManager.getTypeIcon(type);
    }
    const icons = {
        'contract_expiring': 'fas fa-exclamation-triangle text-warning',
        'contract_expired': 'fas fa-times-circle text-danger',
        'system': 'fas fa-info-circle text-info',
        'user': 'fas fa-user text-primary',
        'report': 'fas fa-chart-bar text-success',
        'default': 'fas fa-bell text-secondary'
    };
    
    return icons[type] || icons['default'];
}

function getTimeAgo(dateString) {
    if (window.notificationManager) {
        return window.notificationManager.getTimeAgo(dateString);
    }
    const now = new Date();
    const date = new Date(dateString);
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Hace unos segundos';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    } else if (diffInSeconds < 2592000) {
        const days = Math.floor(diffInSeconds / 86400);
        return `Hace ${days} día${days > 1 ? 's' : ''}`;
    } else {
        return date.toLocaleDateString('es-ES');
    }
}

function markAsRead(notificationId) {
    if (window.notificationManager) {
        window.notificationManager.markAsRead(notificationId);
    }
}

function markAllAsRead() {
    if (window.notificationManager) {
        window.notificationManager.markAllAsRead();
    }
}

function updateNotificationBadge() {
    if (window.notificationManager) {
        window.notificationManager.updateNotificationCount();
    }
}

function showNotificationToast(message) {
    // Crear toast si no existe
    if (!document.getElementById('notificationToast')) {
        const toastHTML = `
            <div class="toast-container position-fixed top-0 end-0 p-3">
                <div id="notificationToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <i class="fas fa-bell me-2"></i>
                        <strong class="me-auto">Notificaciones</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body" id="toastMessage">
                        ${message}
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', toastHTML);
    } else {
        document.getElementById('toastMessage').textContent = message;
    }
    
    const toast = new bootstrap.Toast(document.getElementById('notificationToast'));
    toast.show();
}

// Inicializar el gestor de notificaciones cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    window.notificationManager = new NotificationManager();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (window.notificationManager) {
        window.notificationManager.stopPolling();
    }
});