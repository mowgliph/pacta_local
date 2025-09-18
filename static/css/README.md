# Sistema de Estilos PACTA - Documentación

## Visión General

Este directorio contiene los estilos CSS refactorizados para la aplicación PACTA. La nueva estructura sigue una arquitectura modular y escalable que facilita el mantenimiento y la consistencia visual en toda la aplicación.

## Estructura de Directorios

```
css/refactor/
├── base/             # Estilos base y configuraciones globales
├── components/       # Componentes reutilizables
├── layout/           # Estructuras de diseño
├── pages/            # Estilos específicos de páginas
└── main.css          # Punto de entrada principal
```

## Guía de Estilos

### 1. Base

Contiene los estilos fundamentales que se aplican a toda la aplicación:

- `_variables.css`: Variables CSS globales (colores, tipografía, espaciados, etc.)
- `_accessibility.css`: Mejoras de accesibilidad
- `_scrollbar.css`: Personalización de barras de desplazamiento
- `_focus.css`: Estilos para el foco de accesibilidad

### 2. Componentes

Componentes UI reutilizables. Cada componente debe ser independiente y autocontenido.

**Estructura recomendada para cada componente:**

```css
/* Nombre del componente */
.componente {
  /* Estilos base */
  
  /* Variantes */
  &--variante {
    /* Estilos específicos de la variante */
  }
  
  /* Estados */
  &:hover,
  &:focus {
    /* Estilos de interacción */
  }
  
  /* Elementos hijos */
  &__elemento {
    /* Estilos del elemento hijo */
  }
}
```

### 3. Layout

Estructuras de diseño principales de la aplicación:

- `_grid.css`: Sistema de cuadrícula
- `_container.css`: Contenedores y wrappers
- `_header.css`: Cabecera de la aplicación
- `_sidebar.css`: Barra lateral
- `_footer.css`: Pie de página

### 4. Páginas

Estilos específicos para páginas individuales. Deben usarse con moderación, prefiriendo siempre componentes reutilizables.

## Convenciones de Nombrado

- **BEM (Block Element Modifier)**: Se utiliza la metodología BEM para nombrar las clases
  - `.bloque` - El componente principal
  - `.bloque__elemento` - Un elemento dentro del bloque
  - `.bloque--modificador` - Una variante del bloque

- **Utilidades**: Usar prefijos descriptivos
  - `.u-text-center` - Utilidad para centrar texto
  - `.u-mt-4` - Utilidad de margen superior

## Variables CSS

Las variables se definen en `_variables.css` y siguen esta estructura:

```css
:root {
  /* Colores */
  --color-primary: #A7C7E7;
  --color-primary-light: #C1D9F0;
  
  /* Tipografía */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-base: 1rem;
  
  /* Espaciado */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  /* ... */
}
```

## Buenas Prácticas

1. **Siempre usa variables** para colores, espaciados y tipografía
2. **Evita anidamientos profundos** en los selectores (máximo 3 niveles)
3. **Comenta tu código** para explicar propósitos no obvios
4. **Sigue el principio de responsabilidad única** - cada archivo debe tener un propósito claro
5. **Usa clases de utilidad** para estilos comunes
6. **Evita los estilos en línea** y los `!important`

## Proceso de Desarrollo

1. **Nuevos componentes**:
   - Crea un nuevo archivo en la carpeta `components/`
   - Sigue la convención de nomenclatura BEM
   - Documenta el componente con comentarios

2. **Modificaciones**:
   - Actualiza las variables en `_variables.css` cuando sea posible
   - Si el cambio es específico de un componente, modifica ese archivo
   - Si es un cambio global, actualiza el archivo base correspondiente

3. **Depuración**:
   - Usa las herramientas de desarrollo del navegador
   - Verifica la especificidad de los selectores
   - Asegúrate de que no haya estilos en conflicto

## Compatibilidad

- Navegadores modernos (últimas 2 versiones)
- Soporte para IE11 (si es necesario, usar polyfills)
- Diseño responsivo (mobile-first)

## Recursos

- [Guía de estilos CSS](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Metodología BEM](https://en.bem.info/methodology/)
- [Documentación de CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

## Mantenimiento

- Revisar periódicamente las dependencias
- Actualizar las variables de diseño según sea necesario
- Documentar cambios importantes en el CHANGELOG.md

## Licencia

© 2025 PACTA - Todos los derechos reservados
