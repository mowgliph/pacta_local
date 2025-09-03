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
 * Crea un nuevo usuario enviando los datos al servidor
 */
function createNewUser() {
    const form = document.getElementById('newUserForm');
    
    const userData = {
        nombre: document.getElementById('newUserNombre').value.trim(),
        email: document.getElementById('newUserEmail').value.trim(),
        username: document.getElementById('newUserEmail').value.trim(), // Usar email como username por defecto
        cargo: document.getElementById('newUserCargo').value.trim(),
        telefono: document.getElementById('newUserTelefono').value.trim(),
        password: document.getElementById('newUserPassword').value,
        departamento: document.getElementById('newUserCargo').value.trim(), // Usar cargo como departamento
        es_admin: document.getElementById('newUserRole').value === 'admin' ? 'on' : ''
    };
    
    // Validar campos requeridos
    if (!userData.nombre || !userData.email || !userData.password) {
        alert('Por favor complete todos los campos requeridos (Nombre, Email y Contraseña)');
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