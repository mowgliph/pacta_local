# Componente de Modal de Confirmación Reutilizable

## Descripción

Este componente proporciona un sistema de modales de confirmación consistente y reutilizable para toda la aplicación PACTA. Incluye funciones especializadas para diferentes tipos de confirmaciones y un diseño moderno y accesible.

## Características

- ✅ **Diseño consistente**: Interfaz unificada en toda la aplicación
- ✅ **Totalmente personalizable**: Títulos, mensajes, botones e iconos configurables
- ✅ **Funciones especializadas**: Para eliminación, guardado, envío y advertencias
- ✅ **Responsive**: Adaptado para dispositivos móviles y desktop
- ✅ **Accesible**: Cumple con estándares de accesibilidad web
- ✅ **Fácil integración**: Se carga automáticamente en toda la aplicación

## Instalación

El componente se carga automáticamente en el template base (`base.html`), por lo que está disponible en todas las páginas de la aplicación sin configuración adicional.

## Funciones Disponibles

### 1. `showConfirmModal()` - Función Principal

```javascript
showConfirmModal(
    message,           // string: Mensaje HTML del modal
    onConfirm,         // function: Callback de confirmación
    onCancel,          // function|null: Callback de cancelación (opcional)
    confirmText,       // string: Texto del botón confirmar (default: 'Confirmar')
    cancelText,        // string: Texto del botón cancelar (default: 'Cancelar')
    title,             // string: Título del modal (default: '¿Está seguro?')
    confirmButtonClass,// string: Clase CSS del botón (default: 'btn-danger')
    icon              // string: Icono FontAwesome (default: 'fa-question')
);
```

**Ejemplo:**
```javascript
showConfirmModal(
    '¿Desea continuar con esta acción?',
    () => {
        console.log('Usuario confirmó');
        // Lógica de confirmación aquí
    },
    () => {
        console.log('Usuario canceló');
    },
    'Sí, continuar',
    'No, cancelar',
    'Confirmar acción',
    'btn-primary',
    'fa-check'
);
```

### 2. `showDeleteConfirmModal()` - Para Eliminaciones

```javascript
showDeleteConfirmModal(
    itemName,    // string: Nombre del elemento a eliminar
    onConfirm,   // function: Callback de confirmación
    onCancel     // function|null: Callback de cancelación (opcional)
);
```

**Ejemplo:**
```javascript
showDeleteConfirmModal(
    'usuario Juan Pérez',
    () => {
        // Lógica para eliminar usuario
        deleteUserFromDatabase(userId);
    }
);
```

### 3. `showSaveConfirmModal()` - Para Guardado

```javascript
showSaveConfirmModal(
    message,     // string: Mensaje personalizado
    onConfirm,   // function: Callback de confirmación
    onCancel     // function|null: Callback de cancelación (opcional)
);
```

**Ejemplo:**
```javascript
showSaveConfirmModal(
    'Los cambios se guardarán permanentemente.',
    () => {
        // Lógica para guardar
        saveFormData();
    }
);
```

### 4. `showSendConfirmModal()` - Para Envíos

```javascript
showSendConfirmModal(
    message,     // string: Mensaje personalizado
    onConfirm,   // function: Callback de confirmación
    onCancel     // function|null: Callback de cancelación (opcional)
);
```

**Ejemplo:**
```javascript
showSendConfirmModal(
    'Se enviará el reporte por correo electrónico.',
    () => {
        // Lógica para enviar
        sendReport();
    }
);
```

### 5. `showWarningConfirmModal()` - Para Advertencias

```javascript
showWarningConfirmModal(
    message,     // string: Mensaje personalizado
    onConfirm,   // function: Callback de confirmación
    onCancel     // function|null: Callback de cancelación (opcional)
);
```

**Ejemplo:**
```javascript
showWarningConfirmModal(
    'Esta acción puede afectar otros usuarios del sistema.',
    () => {
        // Lógica para continuar con la acción
        performRiskyAction();
    }
);
```

## Casos de Uso Comunes

### Eliminación de Registros
```javascript
function deleteRecord(id, name) {
    showDeleteConfirmModal(
        `registro "${name}"`,
        () => {
            fetch(`/api/records/${id}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        showToast('Registro eliminado exitosamente', 'success');
                        refreshTable();
                    }
                });
        }
    );
}
```

### Confirmación de Formularios
```javascript
function submitForm() {
    showSaveConfirmModal(
        'Se guardarán todos los cambios realizados.',
        () => {
            document.getElementById('myForm').submit();
        }
    );
}
```

### Acciones Peligrosas
```javascript
function resetSystem() {
    showWarningConfirmModal(
        'Esta acción reiniciará todo el sistema y desconectará a todos los usuarios.',
        () => {
            fetch('/api/system/reset', { method: 'POST' });
        }
    );
}
```

## Personalización de Estilos

El componente utiliza las variables CSS del sistema PACTA. Para personalizar los estilos:

```css
/* En tu archivo CSS personalizado */
.modal-content {
    --border-radius: 16px; /* Bordes más redondeados */
}

.modal-header {
    --bg-color: #your-color; /* Color de fondo personalizado */
}
```

## Integración con Otros Componentes

### Con Sistema de Toasts
```javascript
showDeleteConfirmModal(
    'usuario',
    () => {
        showToast('Eliminando usuario...', 'info');
        
        deleteUser().then(() => {
            showToast('Usuario eliminado exitosamente', 'success');
        }).catch(() => {
            showToast('Error al eliminar usuario', 'error');
        });
    }
);
```

### Con Validaciones
```javascript
function saveWithValidation() {
    if (!validateForm()) {
        showToast('Por favor complete todos los campos requeridos', 'warning');
        return;
    }
    
    showSaveConfirmModal(
        'Los datos han sido validados correctamente.',
        () => {
            saveData();
        }
    );
}
```

## Mejores Prácticas

1. **Usa funciones específicas**: Prefiere `showDeleteConfirmModal()` sobre `showConfirmModal()` para eliminaciones
2. **Mensajes claros**: Describe claramente qué acción se realizará
3. **Callbacks simples**: Mantén la lógica de los callbacks lo más simple posible
4. **Manejo de errores**: Siempre incluye manejo de errores en los callbacks
5. **Feedback visual**: Combina con el sistema de toasts para dar feedback al usuario

## Migración desde confirm() Nativo

### Antes:
```javascript
if (confirm('¿Eliminar usuario?')) {
    deleteUser();
}
```

### Después:
```javascript
showDeleteConfirmModal(
    'usuario',
    () => {
        deleteUser();
    }
);
```

## Soporte y Mantenimiento

- **Archivo principal**: `/static/js/confirm_modal.js`
- **Carga automática**: Se incluye en `templates/base.html`
- **Dependencias**: Bootstrap 5, FontAwesome 6
- **Compatibilidad**: Todos los navegadores modernos

## Changelog

### v1.0.0 (2025)
- ✅ Implementación inicial del componente
- ✅ Funciones especializadas para diferentes casos de uso
- ✅ Integración con el sistema de diseño PACTA
- ✅ Documentación completa y ejemplos de uso