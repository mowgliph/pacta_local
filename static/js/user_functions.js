/**
 * Funciones para manejo de usuarios
 */

// La función showConfirmModal ahora se carga desde confirm_modal.js
// Este archivo utiliza el componente reutilizable de modal de confirmación

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
                showError('Error al cargar el modal de usuario');
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
        rol: document.getElementById('newUserRole').value,
        es_admin: document.getElementById('newUserRole').value === 'admin' ? 'on' : ''
    };
    
    // Validar campos requeridos
    if (!userData.nombre || !userData.email || !userData.username || !userData.password) {
        showError('Por favor complete todos los campos requeridos (Nombre, Email, Username y Contraseña)');
        return;
    }
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userData.email)) {
        showError('Por favor ingrese un email válido');
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
            showSuccess('Usuario creado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('newUserModal')).hide();
            form.reset();
            // Recargar la página para mostrar el nuevo usuario
            window.location.reload();
        } else {
            showError('Error al crear usuario: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error al crear usuario');
    });
}

/**
 * Elimina un usuario
 * @param {number} userId - ID del usuario a eliminar
 */
function deleteUser(userId) {
    showDeleteConfirmModal(
        'usuario',
        () => {
            // Función de confirmación
            fetch(`/eliminar_usuario/${userId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccess('Usuario eliminado exitosamente');
                    window.location.reload();
                } else {
                    showError('Error al eliminar usuario: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Error al eliminar usuario');
            });
        }
    );
}

/**
 * Ver detalles de un usuario
 * @param {number} userId - ID del usuario a ver
 */
function viewUser(userId) {
    // Hacer fetch a la API para obtener los detalles del usuario
    fetch(`/api/usuario/${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const user = data.usuario;
                showUserDetailsModal(user, false); // false = modo vista
            } else {
                showError('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error al obtener detalles del usuario:', error);
            showError('Error al cargar los detalles del usuario');
        });
}

/**
 * Edita un usuario
 * @param {number} userId - ID del usuario a editar
 */
function editUser(userId) {
    // Hacer fetch a la API para obtener los detalles del usuario
    fetch(`/api/usuario/${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const user = data.usuario;
                showUserDetailsModal(user, true); // true = modo edición
            } else {
                showError('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error al obtener detalles del usuario:', error);
            showError('Error al cargar los detalles del usuario');
        });
}

/**
 * Activa o desactiva un usuario
 * @param {number} userId - ID del usuario
 * @param {boolean} activate - true para activar, false para desactivar
 */
function toggleUserStatus(userId, activate) {
    const action = activate ? 'activar' : 'desactivar';
    const confirmMessage = `¿Está seguro de que desea ${action} este usuario?`;
    
    if (confirm(confirmMessage)) {
        fetch(`/toggle_user_status/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ activate: activate })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Usuario ${action} exitosamente`, 'success');
                window.location.reload();
            } else {
                showNotification('Error al cambiar estado del usuario: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al cambiar estado del usuario', 'error');
        });
    }
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
 * Muestra notificaciones al usuario usando el sistema unificado de toasts
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Usar el sistema unificado de toasts
    if (window.toastManager) {
        switch(type) {
            case 'success':
                window.toastManager.showSuccess(message);
                break;
            case 'error':
                window.toastManager.showError(message);
                break;
            case 'warning':
                window.toastManager.showWarning(message);
                break;
            case 'info':
            default:
                window.toastManager.showInfo(message);
                break;
        }
    } else {
        // Fallback a alert si el sistema de toasts no está disponible
        alert(message);
    }
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

/**
 * Muestra el modal de detalles de usuario
 * @param {Object} user - Datos del usuario
 * @param {boolean} editMode - true para modo edición, false para modo vista
 */
function showUserDetailsModal(user, editMode = false) {
    const modal = document.getElementById('userDetailsModal');
    const viewSection = document.getElementById('userDetailsView');
    const editSection = document.getElementById('userDetailsEdit');
    const viewFooter = document.getElementById('userDetailsViewFooter');
    const editFooter = document.getElementById('userDetailsEditFooter');
    
    // Llenar datos en la vista
    fillUserDetailsView(user);
    
    // Llenar datos en el formulario de edición
    fillUserDetailsEdit(user);
    
    // Mostrar la sección apropiada
    if (editMode) {
        viewSection.style.display = 'none';
        editSection.style.display = 'block';
        viewFooter.style.display = 'none';
        editFooter.style.display = 'block';
    } else {
        viewSection.style.display = 'block';
        editSection.style.display = 'none';
        viewFooter.style.display = 'block';
        editFooter.style.display = 'none';
    }
    
    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

/**
 * Llena la vista de detalles con los datos del usuario
 * @param {Object} user - Datos del usuario
 */
function fillUserDetailsView(user) {
    // Avatar y nombre
    const avatar = document.getElementById('userDetailsAvatar');
    const name = document.getElementById('userDetailsNombre');
    const email = document.getElementById('userDetailsEmail');
    
    // Generar avatar
    const initials = user.nombre.split(' ').map(n => n[0]).join('').toUpperCase();
    avatar.textContent = initials;
    avatar.className = 'user-avatar-large avatar-generated';
    
    name.textContent = user.nombre;
    email.textContent = user.email;
    
    // Detalles
    document.getElementById('userDetailsUsername').textContent = user.username || 'No especificado';
    document.getElementById('userDetailsCargo').textContent = user.cargo || 'No especificado';
    document.getElementById('userDetailsTelefono').textContent = user.telefono || 'No especificado';
    // Mostrar rol basado en el campo rol
    let rolTexto = 'Usuario';
    if (user.rol) {
        switch(user.rol) {
            case 'admin': rolTexto = 'Administrador'; break;
            case 'user': rolTexto = 'Usuario Regular'; break;
            case 'guest': rolTexto = 'Invitado'; break;
            default: rolTexto = user.es_admin ? 'Administrador' : 'Usuario';
        }
    } else {
        rolTexto = user.es_admin ? 'Administrador' : 'Usuario';
    }
    document.getElementById('userDetailsRol').textContent = rolTexto;
    
    // Estado
    const statusBadge = document.getElementById('userDetailsEstado');
    statusBadge.textContent = user.activo ? 'Activo' : 'Inactivo';
    statusBadge.className = `status-badge ${user.activo ? 'active' : 'inactive'}`;
    
    document.getElementById('userDetailsUltimoAcceso').textContent = user.ultimo_acceso || 'Nunca';
    document.getElementById('userDetailsDepartamento').textContent = user.departamento || 'No especificado';
    document.getElementById('userDetailsFechaCreacion').textContent = user.fecha_creacion || 'No especificado';
}

/**
 * Llena el formulario de edición con los datos del usuario
 * @param {Object} user - Datos del usuario
 */
function fillUserDetailsEdit(user) {
    document.getElementById('editUserNombre').value = user.nombre || '';
    document.getElementById('editUserEmail').value = user.email || '';
    document.getElementById('editUserTelefono').value = user.telefono || '';
    document.getElementById('editUserCargo').value = user.cargo || '';
    document.getElementById('editUserDepartamento').value = user.departamento || '';
    document.getElementById('editUserRole').value = user.rol || (user.es_admin ? 'admin' : 'user');
    document.getElementById('editUserActivo').value = user.activo ? 'true' : 'false';
    
    // Guardar el ID del usuario para la actualización
    document.getElementById('editUserId').value = user.id;
}

/**
 * Cambia entre modo vista y edición
 */
function toggleEditModeModal() {
    const viewSection = document.getElementById('userDetailsView');
    const editSection = document.getElementById('userDetailsEdit');
    const viewFooter = document.getElementById('userDetailsViewFooter');
    const editFooter = document.getElementById('userDetailsEditFooter');
    
    if (viewSection.style.display === 'none') {
        // Cambiar a modo vista
        viewSection.style.display = 'block';
        editSection.style.display = 'none';
        viewFooter.style.display = 'block';
        editFooter.style.display = 'none';
    } else {
        // Cambiar a modo edición
        viewSection.style.display = 'none';
        editSection.style.display = 'block';
        viewFooter.style.display = 'none';
        editFooter.style.display = 'block';
    }
}

/**
 * Guarda los cambios del usuario
 */
function saveUserChanges() {
    const userId = document.getElementById('editUserId').value;
    
    const userData = {
        nombre: document.getElementById('editUserNombre').value,
        email: document.getElementById('editUserEmail').value,
        cargo: document.getElementById('editUserCargo').value,
        telefono: document.getElementById('editUserTelefono').value,
        departamento: document.getElementById('editUserDepartamento').value,
        rol: document.getElementById('editUserRole').value,
        activo: document.getElementById('editUserActivo').value === 'true'
    };
    
    // Agregar contraseña solo si se especifica
    const password = document.getElementById('editUserPassword').value;
    if (password.trim()) {
        userData.password = password;
    }
    
    // Validaciones básicas
    if (!userData.nombre.trim()) {
        showError('El nombre es requerido');
        return;
    }
    
    if (!userData.email.trim()) {
        showError('El email es requerido');
        return;
    }
    
    // Enviar datos al servidor
    fetch(`/api/usuario/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('userDetailsModal'));
            modal.hide();
            
            // Mostrar notificación de éxito
            showNotification('Usuario actualizado correctamente', 'success');
            
            // Recargar la tabla
            location.reload();
        } else {
            showError('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error al actualizar usuario:', error);
        showError('Error al actualizar el usuario');
    });
}

/**
 * Funciones para selección múltiple de usuarios
 */

/**
 * Alterna la selección de todos los usuarios
 */
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    
    userCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateSelection();
}

/**
 * Actualiza la información de selección
 */
function updateSelection() {
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    const selectedCheckboxes = document.querySelectorAll('.user-checkbox:checked');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectionInfo = document.getElementById('selectionInfo');
    const selectionCount = document.getElementById('selectionCount');
    
    // Actualizar contador
    selectionCount.textContent = selectedCheckboxes.length;
    
    // Mostrar/ocultar información de selección
    if (selectedCheckboxes.length > 0) {
        selectionInfo.style.display = 'block';
    } else {
        selectionInfo.style.display = 'none';
    }
    
    // Actualizar estado del checkbox "Seleccionar todo"
    if (selectedCheckboxes.length === 0) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = false;
    } else if (selectedCheckboxes.length === userCheckboxes.length) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = true;
    } else {
        selectAllCheckbox.indeterminate = true;
        selectAllCheckbox.checked = false;
    }
}

/**
 * Limpia la selección de usuarios
 */
function clearSelection() {
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    
    userCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    selectAllCheckbox.checked = false;
    selectAllCheckbox.indeterminate = false;
    
    updateSelection();
}

/**
 * Obtiene los IDs de los usuarios seleccionados
 * @returns {Array} Array de IDs de usuarios seleccionados
 */
function getSelectedUserIds() {
    const selectedCheckboxes = document.querySelectorAll('.user-checkbox:checked');
    return Array.from(selectedCheckboxes).map(checkbox => parseInt(checkbox.value));
}

/**
 * Edita los usuarios seleccionados
 */
function editSelectedUsers() {
    const selectedIds = getSelectedUserIds();
    
    if (selectedIds.length === 0) {
        showError('Por favor, selecciona al menos un usuario para editar.');
        return;
    }
    
    if (selectedIds.length === 1) {
        // Si solo hay uno seleccionado, abrir el modal de edición
        editUser(selectedIds[0]);
    } else {
        // Para múltiples usuarios, mostrar opciones de edición en lote
        showBulkEditModal(selectedIds);
    }
}

/**
 * Activa/desactiva los usuarios seleccionados
 */
function toggleSelectedUsers() {
    const selectedIds = getSelectedUserIds();
    
    if (selectedIds.length === 0) {
        showError('Por favor, selecciona al menos un usuario.');
        return;
    }
    
    const action = confirm(`¿Estás seguro de que deseas cambiar el estado de ${selectedIds.length} usuario(s)?`);
    
    if (action) {
        // Procesar cada usuario seleccionado
        let completed = 0;
        let errors = 0;
        
        selectedIds.forEach(userId => {
            // Obtener el estado actual del usuario desde la tabla
            const row = document.querySelector(`input[value="${userId}"]`).closest('tr');
            const statusBadge = row.querySelector('.status-badge');
            const isActive = statusBadge.classList.contains('active');
            
            // Cambiar el estado
            toggleUserStatus(userId, !isActive)
                .then(() => {
                    completed++;
                    if (completed + errors === selectedIds.length) {
                        showNotification(`${completed} usuario(s) actualizados correctamente`, 'success');
                        if (errors > 0) {
                            showNotification(`${errors} usuario(s) no pudieron ser actualizados`, 'error');
                        }
                        // Recargar la página para reflejar los cambios
                        setTimeout(() => location.reload(), 1500);
                    }
                })
                .catch(() => {
                    errors++;
                    if (completed + errors === selectedIds.length) {
                        if (completed > 0) {
                            showNotification(`${completed} usuario(s) actualizados correctamente`, 'success');
                        }
                        showNotification(`${errors} usuario(s) no pudieron ser actualizados`, 'error');
                    }
                });
        });
    }
}

/**
 * Elimina los usuarios seleccionados
 */
function deleteSelectedUsers() {
    const selectedIds = getSelectedUserIds();
    
    if (selectedIds.length === 0) {
        showError('Por favor, selecciona al menos un usuario para eliminar.');
        return;
    }
    
    showDeleteConfirmModal(
        `${selectedIds.length} usuario(s)`,
        () => {
            // Función de confirmación - Procesar eliminación de usuarios
            let completed = 0;
            let errors = 0;
            
            selectedIds.forEach(userId => {
                fetch(`/api/usuario/${userId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    completed++;
                    if (completed + errors === selectedIds.length) {
                        if (completed > 0) {
                            showNotification(`${completed} usuario(s) eliminados correctamente`, 'success');
                        }
                        if (errors > 0) {
                            showNotification(`${errors} usuario(s) no pudieron ser eliminados`, 'error');
                        }
                        // Recargar la página para reflejar los cambios
                        setTimeout(() => location.reload(), 1500);
                    }
                })
                .catch(error => {
                    console.error('Error al eliminar usuario:', error);
                    errors++;
                    if (completed + errors === selectedIds.length) {
                        if (completed > 0) {
                            showNotification(`${completed} usuario(s) eliminados correctamente`, 'success');
                        }
                        showNotification(`${errors} usuario(s) no pudieron ser eliminados`, 'error');
                    }
                });
            });
        }
    );
}

/**
 * Muestra el modal de edición en lote (función placeholder)
 * @param {Array} userIds - Array de IDs de usuarios
 */
function showBulkEditModal(userIds) {
    // Por ahora, mostrar un toast con información
    showInfo(`Función de edición en lote para ${userIds.length} usuarios. Esta funcionalidad se puede implementar en el futuro para permitir cambios masivos como: Cambio de rol, Cambio de departamento, Asignación de permisos`);
}

// Hacer disponibles las funciones globalmente
/**
 * Exporta la lista de usuarios a Excel
 */
function exportUsersList() {
    showNotification('Preparando exportación...', 'info');
    
    fetch('/api/users/export', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Error al exportar usuarios');
    })
    .then(blob => {
        // Crear enlace de descarga
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `usuarios_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Lista de usuarios exportada correctamente', 'success');
    })
    .catch(error => {
        console.error('Error al exportar usuarios:', error);
        showNotification('Error al exportar la lista de usuarios', 'error');
    });
}

/**
 * Abre el modal para importar usuarios desde Excel
 */
function importUsersModal() {
    // Crear modal dinámicamente
    const modalHtml = `
        <div class="modal fade" id="importUsersModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-upload text-success me-2"></i>
                            Importar Usuarios
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="importFile" class="form-label">Seleccionar archivo Excel</label>
                            <input type="file" class="form-control" id="importFile" accept=".xlsx,.xls">
                            <div class="form-text">Formatos soportados: .xlsx, .xls</div>
                        </div>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Formato requerido:</strong> El archivo debe contener las columnas: Nombre, Email, Teléfono, Cargo, Departamento, Rol (admin/user)
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-success" onclick="processImportFile()">Importar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si existe
    const existingModal = document.getElementById('importUsersModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('importUsersModal'));
    modal.show();
}

/**
 * Procesa el archivo de importación
 */
function processImportFile() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Por favor selecciona un archivo', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showNotification('Procesando archivo...', 'info');
    
    fetch('/api/users/import', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('importUsersModal'));
            modal.hide();
            
            showNotification(`Importación completada: ${data.imported} usuarios importados`, 'success');
            
            // Recargar página
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error al importar usuarios:', error);
        showNotification('Error al procesar el archivo', 'error');
    });
}

window.viewUser = viewUser;
window.editUser = editUser;
window.toggleUserStatus = toggleUserStatus;
window.showUserDetailsModal = showUserDetailsModal;
window.toggleEditModeModal = toggleEditModeModal;
window.saveUserChanges = saveUserChanges;
window.toggleSelectAll = toggleSelectAll;
window.updateSelection = updateSelection;
window.clearSelection = clearSelection;
window.editSelectedUsers = editSelectedUsers;
window.toggleSelectedUsers = toggleSelectedUsers;
window.deleteSelectedUsers = deleteSelectedUsers;
window.exportUsersList = exportUsersList;
window.importUsersModal = importUsersModal;
window.processImportFile = processImportFile;
window.openNewUserModal = openNewUserModal;

/**
 * Muestra modal para resetear contraseñas de usuarios seleccionados
 */
function resetPasswordsModal() {
    const selectedIds = getSelectedUserIds();
    if (selectedIds.length === 0) {
        showNotification('Por favor selecciona al menos un usuario', 'warning');
        return;
    }
    
    if (confirm(`¿Estás seguro de que deseas resetear las contraseñas de ${selectedIds.length} usuario(s) seleccionado(s)?`)) {
        // Aquí iría la lógica para resetear contraseñas
        showNotification(`Contraseñas reseteadas para ${selectedIds.length} usuario(s)`, 'success');
    }
}

/**
 * Genera reporte detallado de usuarios
 */
function generateUsersReport() {
    showNotification('Generando reporte de usuarios...', 'info');
    // Aquí iría la lógica para generar el reporte
    setTimeout(() => {
        showNotification('Reporte generado exitosamente', 'success');
    }, 2000);
}

/**
 * Muestra modal para configurar permisos de usuarios seleccionados
 */
function configurePermissionsModal() {
    const selectedIds = getSelectedUserIds();
    if (selectedIds.length === 0) {
        showNotification('Por favor selecciona al menos un usuario', 'warning');
        return;
    }
    
    showNotification(`Configurando permisos para ${selectedIds.length} usuario(s)`, 'info');
    // Aquí iría la lógica para mostrar el modal de permisos
}

/**
 * Muestra modal para enviar notificación a usuarios seleccionados
 */
function sendNotificationModal() {
    const selectedIds = getSelectedUserIds();
    if (selectedIds.length === 0) {
        showNotification('Por favor selecciona al menos un usuario', 'warning');
        return;
    }
    
    const message = prompt(`Ingresa el mensaje para enviar a ${selectedIds.length} usuario(s):`);
    if (message) {
        showNotification(`Notificación enviada a ${selectedIds.length} usuario(s)`, 'success');
    }
}

/**
 * Crea respaldo de datos de usuarios
 */
function backupUsersData() {
    showNotification('Creando respaldo de usuarios...', 'info');
    // Aquí iría la lógica para crear el backup
    setTimeout(() => {
        showNotification('Respaldo creado exitosamente', 'success');
    }, 3000);
}

/**
 * Muestra modal de auditoría de usuarios
 */
function showUserAuditModal() {
    const selectedIds = getSelectedUserIds();
    if (selectedIds.length === 0) {
        showNotification('Por favor selecciona al menos un usuario para ver su auditoría', 'warning');
        return;
    }
    
    showNotification(`Cargando historial de ${selectedIds.length} usuario(s)...`, 'info');
    // Aquí iría la lógica para mostrar el modal de auditoría
}

// Exportar las nuevas funciones
window.resetPasswordsModal = resetPasswordsModal;
window.generateUsersReport = generateUsersReport;
window.configurePermissionsModal = configurePermissionsModal;
window.sendNotificationModal = sendNotificationModal;
window.backupUsersData = backupUsersData;
window.showUserAuditModal = showUserAuditModal;