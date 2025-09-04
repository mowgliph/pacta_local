/**
 * Funciones para manejo de usuarios
 */

/**
 * Abre el modal para crear un nuevo usuario
 */
function openNewUserModal() {
    // Verificar si el modal ya existe en el DOM
    if (!document.getElementById('newUserModal')) {
        // Cargar el modal dinámicamente
        fetch('/components/modals/user_modal')
            .then(response => response.text())
            .then(html => {
                document.body.insertAdjacentHTML('beforeend', html);
                // Mostrar modal después de cargarlo
                const modal = new bootstrap.Modal(document.getElementById('newUserModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error cargando modal:', error);
                alert('Error al cargar el modal de usuario');
            });
    } else {
        // Mostrar modal si ya existe
        const modal = new bootstrap.Modal(document.getElementById('newUserModal'));
        modal.show();
    }
}

/**
 * Genera un username válido basado en el email
 * @param {string} email - Email del usuario
 * @returns {string} Username generado
 */
function generateUsername(email) {
    // Extraer la parte antes del @ del email
    const emailPrefix = email.split('@')[0];
    
    // Limpiar caracteres especiales y convertir a minúsculas
    let username = emailPrefix
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '') // Eliminar caracteres especiales
        .substring(0, 20); // Limitar a 20 caracteres
    
    // Asegurar que no esté vacío
    if (!username) {
        username = 'usuario';
    }
    
    return username;
}

/**
 * Actualiza el campo username basado en el email ingresado
 */
function updateUsernameFromEmail() {
    const emailField = document.getElementById('newUserEmail');
    const usernameField = document.getElementById('newUserUsername');
    
    if (emailField && usernameField && emailField.value) {
        const generatedUsername = generateUsername(emailField.value);
        usernameField.value = generatedUsername;
    }
}

/**
 * Crea un nuevo usuario enviando los datos al servidor
 */
function createNewUser() {
    const form = document.getElementById('newUserForm');
    const email = document.getElementById('newUserEmail').value.trim();
    
    const userData = {
        nombre: document.getElementById('newUserNombre').value.trim(),
        email: email,
        username: document.getElementById('newUserUsername').value.trim(), // Usar username del formulario
        cargo: document.getElementById('newUserCargo').value.trim(),
        telefono: document.getElementById('newUserTelefono').value.trim(),
        password: document.getElementById('newUserPassword').value,
        departamento: document.getElementById('newUserCargo').value.trim(), // Usar cargo como departamento
        es_admin: document.getElementById('newUserRole').value === 'admin' ? 'on' : ''
    };
    
    // Validar campos requeridos
    if (!userData.nombre || !userData.email || !userData.username || !userData.password) {
        alert('Por favor complete todos los campos requeridos (Nombre, Email, Username y Contraseña)');
        return;
    }
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userData.email)) {
        alert('Por favor ingrese un email válido');
        return;
    }
    
    // Crear FormData para enviar como form data (no JSON)
    const formData = new FormData();
    Object.keys(userData).forEach(key => {
        formData.append(key, userData[key]);
    });
    
    // Enviar datos al servidor
    fetch('/crear_usuario', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Usuario creado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('newUserModal')).hide();
            form.reset();
            // Recargar la página para mostrar el nuevo usuario
            window.location.reload();
        } else {
            alert('Error al crear usuario: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al crear usuario');
    });
}

/**
 * Elimina un usuario (función de ejemplo para futuras implementaciones)
 * @param {number} userId - ID del usuario a eliminar
 */
function deleteUser(userId) {
    if (confirm('¿Está seguro de que desea eliminar este usuario?')) {
        fetch(`/eliminar_usuario/${userId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Usuario eliminado exitosamente');
                window.location.reload();
            } else {
                alert('Error al eliminar usuario: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar usuario');
        });
    }
}

/**
 * Edita un usuario (función de ejemplo para futuras implementaciones)
 * @param {number} userId - ID del usuario a editar
 */
function editUser(userId) {
    // Implementar lógica para editar usuario
    console.log('Editando usuario:', userId);
    // Esta función se puede expandir para abrir un modal de edición
}

// ===== FUNCIONES PARA EDICIÓN DE PERFIL =====

let isEditMode = false;

/**
 * Alterna el modo de edición del perfil
 */
function toggleEditMode() {
    const editForm = document.getElementById('editForm');
    const editIcon = document.getElementById('editIcon');
    
    if (!isEditMode) {
        // Entrar en modo edición
        editForm.style.display = 'block';
        editIcon.className = 'fas fa-times';
        isEditMode = true;
    } else {
        // Salir del modo edición
        cancelEdit();
    }
}

/**
 * Cancela la edición del perfil
 */
function cancelEdit() {
    const editForm = document.getElementById('editForm');
    const editIcon = document.getElementById('editIcon');
    
    editForm.style.display = 'none';
    editIcon.className = 'fas fa-edit';
    isEditMode = false;
    
    // Limpiar campos de contraseña
    const passwordActual = document.getElementById('passwordActual');
    const nuevaPassword = document.getElementById('nuevaPassword');
    const confirmarPassword = document.getElementById('confirmarPassword');
    
    if (passwordActual) passwordActual.value = '';
    if (nuevaPassword) nuevaPassword.value = '';
    if (confirmarPassword) confirmarPassword.value = '';
    
    // Resetear formulario a valores originales
    resetFormToOriginalValues();
}

/**
 * Resetea el formulario a valores originales
 */
function resetFormToOriginalValues() {
    // Esta función se puede expandir para resetear todos los campos
    // Por ahora, los valores originales ya están en el HTML
}

/**
 * Guarda los cambios del perfil
 */
function saveChanges() {
    const form = document.getElementById('profileForm');
    const formData = new FormData(form);
    
    // Validaciones del lado cliente
    const nombre = formData.get('nombre').trim();
    const email = formData.get('email').trim();
    const nuevaPassword = formData.get('nueva_password');
    const confirmarPassword = formData.get('confirmar_password');
    
    if (!nombre) {
        showNotification('El nombre es obligatorio', 'error');
        return;
    }
    
    if (!email) {
        showNotification('El email es obligatorio', 'error');
        return;
    }
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showNotification('Formato de email inválido', 'error');
        return;
    }
    
    // Validar contraseñas si se están cambiando
    if (nuevaPassword || confirmarPassword) {
        if (nuevaPassword !== confirmarPassword) {
            showNotification('Las contraseñas no coinciden', 'error');
            return;
        }
        
        if (nuevaPassword.length < 6) {
            showNotification('La contraseña debe tener al menos 6 caracteres', 'error');
            return;
        }
    }
    
    // Mostrar indicador de carga
    const saveButton = document.querySelector('button[onclick="saveChanges()"]');
    const originalText = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 8px;"></i>Guardando...';
    saveButton.disabled = true;
    
    // Enviar datos al servidor
    fetch('/editar_perfil', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            
            // Actualizar la información mostrada en la página
            updateDisplayedUserInfo(data.usuario);
            
            // Salir del modo edición
            cancelEdit();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al actualizar el perfil', 'error');
    })
    .finally(() => {
        // Restaurar botón
        saveButton.innerHTML = originalText;
        saveButton.disabled = false;
    });
}

/**
 * Actualiza la información mostrada en la página
 * @param {Object} usuario - Datos del usuario actualizado
 */
function updateDisplayedUserInfo(usuario) {
    // Actualizar nombre en el header
    const userNameElements = document.querySelectorAll('.user-name-small, h2');
    userNameElements.forEach(element => {
        if (element.tagName === 'H2') {
            element.textContent = usuario.nombre;
        } else {
            element.textContent = usuario.nombre;
        }
    });
    
    // Actualizar email
    const emailElement = document.getElementById('userEmail');
    if (emailElement) {
        emailElement.textContent = usuario.email;
    }
    
    // Actualizar teléfono
    const phoneElement = document.getElementById('userPhone');
    if (phoneElement) {
        phoneElement.textContent = usuario.telefono || 'No especificado';
    }
    
    // Actualizar cargo
    const cargoElements = document.querySelectorAll('p[style*="color: #6b7280"]');
    cargoElements.forEach(element => {
        if (element.textContent.includes('Gerente') || element.textContent.includes('cargo')) {
            element.textContent = usuario.cargo || 'No especificado';
        }
    });
    
    // Actualizar avatar con iniciales
    updateUserAvatar(usuario.nombre);
}

/**
 * Actualiza el avatar con las iniciales del usuario
 * @param {string} nombre - Nombre del usuario
 */
function updateUserAvatar(nombre) {
    const avatarElements = document.querySelectorAll('.user-avatar-small, .user-avatar-large');
    const initials = getInitials(nombre);
    
    avatarElements.forEach(element => {
        element.textContent = initials;
    });
}

/**
 * Obtiene las iniciales del nombre
 * @param {string} nombre - Nombre completo
 * @returns {string} Iniciales
 */
function getInitials(nombre) {
    if (!nombre) return 'U';
    
    const words = nombre.trim().split(' ');
    if (words.length === 1) {
        return words[0].charAt(0).toUpperCase();
    } else {
        return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase();
    }
}

/**
 * Muestra notificaciones al usuario
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Colores según el tipo
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Icono según el tipo
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; margin-left: 8px; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Añadir al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

/**
 * Configura la validación de contraseñas en tiempo real
 */
function setupPasswordValidation() {
    const nuevaPassword = document.getElementById('nuevaPassword');
    const confirmarPassword = document.getElementById('confirmarPassword');
    
    if (nuevaPassword && confirmarPassword) {
        function validatePasswords() {
            if (nuevaPassword.value && confirmarPassword.value) {
                if (nuevaPassword.value !== confirmarPassword.value) {
                    confirmarPassword.setCustomValidity('Las contraseñas no coinciden');
                } else {
                    confirmarPassword.setCustomValidity('');
                }
            }
        }
        
        nuevaPassword.addEventListener('input', validatePasswords);
        confirmarPassword.addEventListener('input', validatePasswords);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupPasswordValidation();
});

// Función para manejar teclas de escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && isEditMode) {
        cancelEdit();
    }
});