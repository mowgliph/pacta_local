/**
 * Funcionalidad principal para el módulo de Suplementos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Manejar el envío del formulario de creación
    const formCrear = document.getElementById('formCrearSuplemento');
    if (formCrear) {
        formCrear.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarFormulario(formCrear, 'crear');
        });
    }

    // Manejar el envío del formulario de edición
    const formEditar = document.getElementById('formEditarSuplemento');
    if (formEditar) {
        formEditar.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarFormulario(formEditar, 'editar');
        });
    }

    // Manejar la confirmación de eliminación
    const btnConfirmarEliminar = document.getElementById('confirmarEliminar');
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', function() {
            const suplementoId = this.getAttribute('data-suplemento-id');
            if (suplementoId) {
                eliminarSuplemento(suplementoId);
            }
        });
    }

    // Inicializar datepickers
    inicializarDatepickers();

    // Inicializar validaciones
    inicializarValidaciones();
});

/**
 * Envía el formulario vía AJAX
 */
function enviarFormulario(formulario, accion) {
    const formData = new FormData(formulario);
    const url = formulario.getAttribute('action');
    const metodo = formulario.getAttribute('method') || 'POST';
    const boton = formulario.querySelector('button[type="submit"]');
    const textoOriginal = boton.innerHTML;

    // Mostrar indicador de carga
    boton.disabled = true;
    boton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';

    fetch(url, {
        method: metodo,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarMensajeExito(data.message || 'Operación realizada con éxito');
            // Cerrar el modal después de un breve retraso
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(formulario.closest('.modal'));
                if (modal) modal.hide();
                // Recargar la página o actualizar la tabla
                if (typeof recargarTablaSuplementos === 'function') {
                    recargarTablaSuplementos();
                } else {
                    window.location.reload();
                }
            }, 1500);
        } else {
            mostrarMensajeError(data.message || 'Error al procesar la solicitud');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensajeError('Error de conexión. Por favor, intente nuevamente.');
    })
    .finally(() => {
        // Restaurar el botón
        boton.disabled = false;
        boton.innerHTML = textoOriginal;
    });
}

/**
 * Elimina un suplemento
 */
function eliminarSuplemento(suplementoId) {
    if (!confirm('¿Está seguro de que desea eliminar este suplemento? Esta acción no se puede deshacer.')) {
        return;
    }

    const url = `/suplementos/${suplementoId}/eliminar`;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': csrfToken || ''
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarMensajeExito(data.message || 'Suplemento eliminado correctamente');
            // Cerrar el modal de confirmación
            const modal = bootstrap.Modal.getInstance(document.getElementById('eliminarSuplementoModal'));
            if (modal) modal.hide();
            // Recargar la página o actualizar la tabla
            if (typeof recargarTablaSuplementos === 'function') {
                recargarTablaSuplementos();
            } else {
                window.location.reload();
            }
        } else {
            mostrarMensajeError(data.message || 'Error al eliminar el suplemento');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarMensajeError('Error de conexión. Por favor, intente nuevamente.');
    });
}

/**
 * Inicializa los datepickers
 */
function inicializarDatepickers() {
    // Configuración común para todos los datepickers
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Establecer la fecha actual como valor por defecto si no hay valor
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
}

/**
 * Inicializa las validaciones de formularios
 */
function inicializarValidaciones() {
    // Ejemplo de validación para el formulario de creación
    const formCrear = document.getElementById('formCrearSuplemento');
    if (formCrear) {
        formCrear.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        }, false);
    }

    // Ejemplo de validación para el formulario de edición
    const formEditar = document.getElementById('formEditarSuplemento');
    if (formEditar) {
        formEditar.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        }, false);
    }
}

/**
 * Muestra un mensaje de éxito
 */
function mostrarMensajeExito(mensaje) {
    // Implementar lógica para mostrar mensajes de éxito
    // Por ejemplo, usando Toast de Bootstrap
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        const toast = new bootstrap.Toast(document.getElementById('toastExito'));
        const toastBody = document.querySelector('#toastExito .toast-body');
        if (toastBody) {
            toastBody.textContent = mensaje;
            toast.show();
        }
    } else {
        alert(mensaje); // Fallback si no hay contenedor de toasts
    }
}

/**
 * Muestra un mensaje de error
 */
function mostrarMensajeError(mensaje) {
    // Implementar lógica para mostrar mensajes de error
    // Similar a mostrarMensajeExito pero con estilos de error
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        const toast = new bootstrap.Toast(document.getElementById('toastError'));
        const toastBody = document.querySelector('#toastError .toast-body');
        if (toastBody) {
            toastBody.textContent = mensaje;
            toast.show();
        }
    } else {
        alert('Error: ' + mensaje); // Fallback si no hay contenedor de toasts
    }
}

/**
 * Función para recargar la tabla de suplementos (si se usa DataTables)
 */
function recargarTablaSuplementos() {
    const tabla = $('#tablaSuplementos').DataTable();
    if (tabla) {
        tabla.ajax.reload(null, false);
    }
}
