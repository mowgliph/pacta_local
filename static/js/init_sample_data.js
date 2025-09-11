/**
 * Script para inicializar datos de ejemplo en la aplicación PACTA
 * Este script se ejecuta cuando la base de datos está vacía
 */

class SampleDataInitializer {
    constructor() {
        this.apiBase = '/api';
        this.isInitializing = false;
    }

    /**
     * Verifica si la base de datos está vacía
     */
    async checkDatabaseEmpty() {
        try {
            const response = await fetch(`${this.apiBase}/check-database-empty`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.isEmpty;
        } catch (error) {
            console.error('Error verificando base de datos:', error);
            return false;
        }
    }

    /**
     * Crea el usuario administrador
     */
    async createAdminUser() {
        if (this.isInitializing) {
            console.log('Ya se está inicializando...');
            return;
        }

        this.isInitializing = true;
        
        try {
            this.showLoadingMessage('Creando usuario administrador...');
            
            const response = await fetch(`${this.apiBase}/create-admin-user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccessMessage('Usuario administrador creado exitosamente');
                console.log('Admin creado:', result.message);
                
                // Recargar la página después de 2 segundos
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(result.message || 'Error desconocido');
            }
            
        } catch (error) {
            console.error('Error creando usuario admin:', error);
            this.showErrorMessage('Error al crear usuario administrador: ' + error.message);
        } finally {
            this.isInitializing = false;
        }
    }

    /**
     * Inicializa los datos de ejemplo
     */
    async initializeSampleData() {
        if (this.isInitializing) {
            console.log('Ya se está inicializando la base de datos...');
            return;
        }

        this.isInitializing = true;
        
        try {
            this.showLoadingMessage('Inicializando datos de ejemplo...');
            
            const response = await fetch(`${this.apiBase}/initialize-sample-data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccessMessage('Datos de ejemplo creados exitosamente');
                console.log('Datos creados:', result.summary);
                
                // Recargar la página después de 2 segundos
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                throw new Error(result.message || 'Error desconocido');
            }
            
        } catch (error) {
            console.error('Error inicializando datos:', error);
            this.showErrorMessage('Error al crear datos de ejemplo: ' + error.message);
        } finally {
            this.isInitializing = false;
        }
    }

    /**
     * Función de compatibilidad para checkAndInitialize
     */
    async checkAndInitialize() {
        return this.autoInitialize();
    }

    /**
     * Verifica automáticamente si necesita inicializar datos
     */
    async autoInitialize() {
        try {
            const response = await fetch('/api/check-database-empty');
            const data = await response.json();
            
            if (data.success && data.needs_initialization) {
                // Determinar el mensaje según el estado
                let message = '';
                if (data.is_empty) {
                    message = '¿Desea crear datos de ejemplo para comenzar a usar el sistema?';
                } else if (!data.admin_exists) {
                    message = 'Se detectó que no existe un usuario administrador. ¿Desea crear el usuario admin con contraseña "pacta"?';
                }
                
                this.showConfirmationModal(message, data.is_empty, !data.admin_exists);
            } else {
                console.log('Base de datos contiene datos existentes');
            }
        } catch (error) {
            console.error('Error en auto-inicialización:', error);
        }
    }

    /**
     * Muestra modal de confirmación para inicializar datos
     */
    showConfirmationModal(message = '¿Desea crear datos de ejemplo para comenzar a usar la aplicación?', createSampleData = true, createAdmin = false) {
        const modalHtml = `
            <div id="initDataModal" class="modal fade" tabindex="-1" role="dialog" data-backdrop="static">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-database mr-2"></i>
                                Inicializar Base de Datos
                            </h5>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-3">
                                <i class="fas fa-info-circle text-info" style="font-size: 3rem;"></i>
                            </div>
                            <p class="text-center mb-3">
                                ${message}
                            </p>
                            <div class="alert alert-info">
                                <small>
                                    <strong>Los datos de ejemplo incluyen:</strong><br>
                                    • Usuarios de prueba<br>
                                    • Clientes y proveedores<br>
                                    • Contratos de muestra<br>
                                    • Suplementos y notificaciones<br>
                                    • Actividades del sistema
                                </small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" onclick="sampleDataInit.dismissModal()">
                                <i class="fas fa-times mr-1"></i>
                                Continuar sin datos
                            </button>
                            <button type="button" class="btn btn-primary" onclick="sampleDataInit.confirmInitialization(${createSampleData}, ${createAdmin})">
                                <i class="fas fa-plus mr-1"></i>
                                ${createSampleData ? 'Crear datos de ejemplo' : 'Crear usuario admin'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar modal
        $('#initDataModal').modal('show');
    }

    /**
     * Confirma la inicialización de datos
     */
    async confirmInitialization(createSampleData = true, createAdmin = false) {
        $('#initDataModal').modal('hide');
        
        if (createSampleData) {
            await this.initializeSampleData();
        } else if (createAdmin) {
            await this.createAdminUser();
        }
    }

    /**
     * Descarta el modal sin inicializar
     */
    dismissModal() {
        $('#initDataModal').modal('hide');
        
        // Remover modal del DOM después de ocultarlo
        setTimeout(() => {
            const modal = document.getElementById('initDataModal');
            if (modal) {
                modal.remove();
            }
        }, 300);
    }

    /**
     * Muestra mensaje de carga
     */
    showLoadingMessage(message) {
        this.showToast(message, 'info', 0); // 0 = no auto-hide
    }

    /**
     * Muestra mensaje de éxito
     */
    showSuccessMessage(message) {
        this.showToast(message, 'success', 5000);
    }

    /**
     * Muestra mensaje de error
     */
    showErrorMessage(message) {
        this.showToast(message, 'error', 8000);
    }

    /**
     * Muestra toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        // Si existe el toast manager, usarlo
        if (typeof window.toastManager !== 'undefined') {
            window.toastManager.show(message, type, duration);
            return;
        }

        // Fallback: crear toast simple
        const toastId = 'toast-' + Date.now();
        const toastClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'info': 'alert-info',
            'warning': 'alert-warning'
        }[type] || 'alert-info';

        const toastHtml = `
            <div id="${toastId}" class="alert ${toastClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
                ${message}
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', toastHtml);

        // Auto-hide si se especifica duración
        if (duration > 0) {
            setTimeout(() => {
                const toast = document.getElementById(toastId);
                if (toast) {
                    $(toast).alert('close');
                }
            }, duration);
        }
    }
}

// Crear instancia global
const sampleDataInit = new SampleDataInitializer();

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para que la página se cargue completamente
    setTimeout(() => {
        sampleDataInit.autoInitialize();
    }, 1000);
});

// Exportar para uso global
window.sampleDataInit = sampleDataInit;