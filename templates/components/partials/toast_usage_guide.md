# Guía de Uso del Sistema de Toasts Unificado

## Descripción
Este sistema proporciona una forma consistente y fácil de mostrar notificaciones toast en toda la aplicación PACTA.

## Instalación

### 1. Incluir en plantillas HTML
Agregar al final de cualquier plantilla que necesite toasts:

```html
<!-- Incluir el componente de toast -->
{% include 'components/partials/toast_container.html' %}
```

### 2. Asegurar Bootstrap
Verificar que Bootstrap 5 esté cargado antes del toast manager:

```html
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

## Uso Básico

### Funciones Principales

```javascript
// Toast de éxito
showSuccess('Operación completada exitosamente');

// Toast de error
showError('Ha ocurrido un error');

// Toast de advertencia
showWarning('Atención: revisa los datos');

// Toast de información
showInfo('Información importante');

// Función genérica
showNotification('Mensaje', 'success'); // tipos: success, error, warning, info
```

### Duración Personalizada

```javascript
// Con duración personalizada (en milisegundos)
showSuccess('Mensaje', 3000); // 3 segundos
showError('Error crítico', 10000); // 10 segundos
```

### Uso Avanzado

```javascript
// Toast personalizado
window.toastManager.showCustom({
    message: 'Mensaje personalizado',
    type: 'success',
    duration: 5000,
    title: 'Título opcional'
});

// Limpiar todos los toasts
window.toastManager.clearAll();
```

## Migración desde Alerts

### Antes (usando alert)
```javascript
alert('Usuario creado exitosamente');
alert('Error al crear usuario');
```

### Después (usando toasts)
```javascript
showSuccess('Usuario creado exitosamente');
showError('Error al crear usuario');
```

## Tipos de Toast Disponibles

| Tipo | Función | Color | Icono | Duración por defecto |
|------|---------|-------|-------|---------------------|
| Éxito | `showSuccess()` | Verde | ✓ | 5 segundos |
| Error | `showError()` | Rojo | ⚠ | 7 segundos |
| Advertencia | `showWarning()` | Amarillo | ⚠ | 6 segundos |
| Información | `showInfo()` | Azul | ℹ | 5 segundos |

## Ejemplos de Uso en Diferentes Contextos

### En formularios
```javascript
// Validación exitosa
if (formIsValid) {
    showSuccess('Formulario enviado correctamente');
} else {
    showError('Por favor corrige los errores en el formulario');
}
```

### En operaciones AJAX
```javascript
fetch('/api/usuarios', {
    method: 'POST',
    body: JSON.stringify(userData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showSuccess('Usuario creado exitosamente');
    } else {
        showError('Error: ' + data.message);
    }
})
.catch(error => {
    showError('Error de conexión');
});
```

### En operaciones de eliminación
```javascript
function deleteUser(userId) {
    if (confirm('¿Estás seguro de eliminar este usuario?')) {
        // Realizar eliminación
        showSuccess('Usuario eliminado correctamente');
    }
}
```

## Características

- ✅ **Consistente**: Mismo estilo en toda la aplicación
- ✅ **Responsive**: Se adapta a dispositivos móviles
- ✅ **Accesible**: Compatible con lectores de pantalla
- ✅ **Animado**: Transiciones suaves
- ✅ **Configurable**: Duración y tipos personalizables
- ✅ **Auto-limpieza**: Se remueven automáticamente del DOM

## Compatibilidad

- ✅ Bootstrap 5.x
- ✅ Navegadores modernos (Chrome, Firefox, Safari, Edge)
- ✅ Dispositivos móviles
- ✅ Lectores de pantalla

## Notas Importantes

1. **No usar `alert()` nativo**: Reemplazar con toasts para mejor UX
2. **Incluir solo una vez**: El componente debe incluirse solo una vez por página
3. **Bootstrap requerido**: Asegurar que Bootstrap esté cargado
4. **Posición fija**: Los toasts aparecen en la esquina superior derecha

## Solución de Problemas

### Toast no aparece
- Verificar que Bootstrap esté cargado
- Verificar que el componente esté incluido
- Revisar la consola del navegador por errores

### Estilos incorrectos
- Verificar que Bootstrap CSS esté cargado
- Verificar que no haya conflictos de CSS

### Funciones no definidas
- Verificar que `toast_manager.js` esté cargado
- Verificar que el DOM esté completamente cargado

## Personalización

Para personalizar los estilos, modificar el CSS en `toast_container.html` o crear estilos adicionales en tu archivo CSS principal.

```css
/* Ejemplo de personalización */
.toast.bg-success {
    background-color: #custom-color !important;
}
```