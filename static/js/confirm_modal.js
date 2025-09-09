/**
 * Componente de Modal de Confirmación Reutilizable
 * 
 * Este componente proporciona un modal de confirmación consistente y reutilizable
 * para toda la aplicación. Incluye soporte para títulos personalizados,
 * mensajes con formato HTML, y callbacks para confirmación y cancelación.
 * 
 * @author Sistema PACTA
 * @version 1.0
 */

/**
 * Muestra un modal de confirmación personalizable
 * @param {string} message - Mensaje a mostrar en el cuerpo del modal (acepta HTML)
 * @param {function} onConfirm - Función a ejecutar cuando se confirma la acción
 * @param {function|null} onCancel - Función a ejecutar cuando se cancela (opcional)
 * @param {string} confirmText - Texto del botón de confirmación (por defecto: 'Confirmar')
 * @param {string} cancelText - Texto del botón de cancelación (por defecto: 'Cancelar')
 * @param {string} title - Título del modal (por defecto: '¿Está seguro?')
 * @param {string} confirmButtonClass - Clase CSS del botón de confirmación (por defecto: 'btn-danger')
 * @param {string} icon - Icono a mostrar en el título (por defecto: 'fa-question')
 */
function showConfirmModal(
    message, 
    onConfirm, 
    onCancel = null, 
    confirmText = 'Confirmar', 
    cancelText = 'Cancelar', 
    title = '¿Está seguro?',
    confirmButtonClass = 'btn-danger',
    icon = 'fa-question'
) {
    // Crear el modal de confirmación
    const modalId = 'confirmModal-' + Date.now();
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1" role="dialog" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document" style="max-width: 400px;">
                <div class="modal-content" style="border: 1px solid var(--border-light); border-radius: 12px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);">
                    <div class="modal-header" style="background: var(--bg-secondary); border-bottom: 1px solid var(--border-light); padding: 1.5rem;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <div style="width: 24px; height: 24px; background: var(--color-warning-bg); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                <i class="fas ${icon}" style="color: var(--color-warning); font-size: 0.9rem;"></i>
                            </div>
                            <h6 class="modal-title" id="${modalId}Label" style="color: var(--text-primary); font-weight: 500; margin: 0;">
                                ${title}
                            </h6>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar" style="font-size: 0.8rem;"></button>
                    </div>
                    <div class="modal-body" style="padding: 1.5rem;">
                        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0; text-align: left;">${message}</div>
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid var(--border-light); padding: 1rem 1.5rem; gap: 0.75rem; justify-content: flex-end;">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" style="padding: 0.5rem 1.25rem; border-radius: 6px; font-size: 0.9rem;">${cancelText}</button>
                        <button type="button" class="btn ${confirmButtonClass}" id="${modalId}-confirm" style="padding: 0.5rem 1.25rem; border-radius: 6px; font-size: 0.9rem;">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Eliminar modal anterior si existe
    const existingModal = document.querySelector('[id^="confirmModal-"]');
    if (existingModal) {
        existingModal.remove();
    }

    // Agregar el modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Obtener referencias a los elementos
    const modalElement = document.getElementById(modalId);
    const confirmButton = document.getElementById(`${modalId}-confirm`);
    
    // Configurar eventos
    confirmButton.addEventListener('click', () => {
        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
        
        // Ejecutar callback de confirmación
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    // Evento para cancelación
    modalElement.addEventListener('hidden.bs.modal', () => {
        // Ejecutar callback de cancelación si se proporcionó
        if (typeof onCancel === 'function') {
            onCancel();
        }
        
        // Limpiar el modal del DOM
        modalElement.remove();
    });
    
    // Mostrar el modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

/**
 * Funciones de conveniencia para casos de uso comunes
 */

/**
 * Modal de confirmación para eliminación
 * @param {string} itemName - Nombre del elemento a eliminar
 * @param {function} onConfirm - Función a ejecutar al confirmar
 * @param {function|null} onCancel - Función a ejecutar al cancelar (opcional)
 */
function showDeleteConfirmModal(itemName, onConfirm, onCancel = null) {
    const message = `
        <strong>Esta acción no se puede deshacer</strong> y eliminará permanentemente:
        <br><br>
        • Los datos del ${itemName}<br>
        • Su historial de actividades<br>
        • Sus configuraciones asociadas
    `;
    
    showConfirmModal(
        message,
        onConfirm,
        onCancel,
        'Eliminar',
        'Cancelar',
        `¿Eliminar ${itemName}?`,
        'btn-danger',
        'fa-trash'
    );
}

/**
 * Modal de confirmación para acciones de guardado
 * @param {string} message - Mensaje personalizado
 * @param {function} onConfirm - Función a ejecutar al confirmar
 * @param {function|null} onCancel - Función a ejecutar al cancelar (opcional)
 */
function showSaveConfirmModal(message, onConfirm, onCancel = null) {
    showConfirmModal(
        message,
        onConfirm,
        onCancel,
        'Guardar',
        'Cancelar',
        '¿Guardar cambios?',
        'btn-primary',
        'fa-save'
    );
}

/**
 * Modal de confirmación para acciones de envío
 * @param {string} message - Mensaje personalizado
 * @param {function} onConfirm - Función a ejecutar al confirmar
 * @param {function|null} onCancel - Función a ejecutar al cancelar (opcional)
 */
function showSendConfirmModal(message, onConfirm, onCancel = null) {
    showConfirmModal(
        message,
        onConfirm,
        onCancel,
        'Enviar',
        'Cancelar',
        '¿Enviar información?',
        'btn-success',
        'fa-paper-plane'
    );
}

/**
 * Modal de confirmación genérico con advertencia
 * @param {string} message - Mensaje personalizado
 * @param {function} onConfirm - Función a ejecutar al confirmar
 * @param {function|null} onCancel - Función a ejecutar al cancelar (opcional)
 */
function showWarningConfirmModal(message, onConfirm, onCancel = null) {
    showConfirmModal(
        message,
        onConfirm,
        onCancel,
        'Continuar',
        'Cancelar',
        '¡Atención!',
        'btn-warning',
        'fa-exclamation-triangle'
    );
}

// Hacer las funciones disponibles globalmente
window.showConfirmModal = showConfirmModal;
window.showDeleteConfirmModal = showDeleteConfirmModal;
window.showSaveConfirmModal = showSaveConfirmModal;
window.showSendConfirmModal = showSendConfirmModal;
window.showWarningConfirmModal = showWarningConfirmModal;

// Exportar para uso con módulos ES6 si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showConfirmModal,
        showDeleteConfirmModal,
        showSaveConfirmModal,
        showSendConfirmModal,
        showWarningConfirmModal
    };
}