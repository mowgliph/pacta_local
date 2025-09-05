# Arquitectura CSS Modular - PACTA

## 📋 Descripción General

Este proyecto implementa una arquitectura CSS modular y escalable basada en metodologías modernas de desarrollo frontend. La estructura está diseñada para ser mantenible, reutilizable y fácil de escalar.

## 🏗️ Estructura de Carpetas

```
static/css/
├── style.css                 # Archivo principal (punto de entrada único)
├── README.md                 # Esta documentación
├── base/                     # Estilos fundamentales
│   ├── _variables.css        # Variables CSS globales
│   ├── _reset.css           # Reset y normalización
│   ├── _typography.css      # Tipografía base
│   └── _utilities.css       # Clases utilitarias
├── layout/                   # Sistema de layout
│   └── _responsive.css      # Grid y responsive design
├── components/               # Componentes reutilizables
│   ├── _buttons.css         # Estilos de botones
│   ├── _forms.css           # Formularios y inputs
│   ├── _cards.css           # Tarjetas y contenedores
│   └── _tables.css          # Tablas y listas
└── pages/                    # Estilos específicos por página
    ├── dashboard.css        # Panel principal
    ├── contracts.css        # Gestión de contratos
    ├── backup.css           # Sistema de respaldos
    └── changelog.css        # Registro de cambios
```

## 🎯 Principios de Diseño

### 1. **Modularidad**
- Cada archivo tiene una responsabilidad específica
- Los módulos son independientes y reutilizables
- Fácil mantenimiento y debugging

### 2. **Escalabilidad**
- Estructura preparada para crecer
- Nomenclatura consistente
- Variables centralizadas

### 3. **Rendimiento**
- Importaciones optimizadas
- CSS crítico separado
- Estilos de impresión independientes

### 4. **Accesibilidad**
- Soporte para `prefers-reduced-motion`
- Soporte para `prefers-contrast`
- Soporte para `prefers-color-scheme`
- Elementos de navegación accesible

## 🔧 Uso e Implementación

### Importación en HTML

```html
<!-- Solo importar el archivo principal -->
<link rel="stylesheet" href="/static/css/style.css">
```

### Orden de Especificidad

Los archivos se importan en el siguiente orden para mantener la cascada CSS:

1. **Variables** (`_variables.css`) - Definiciones globales
2. **Reset** (`_reset.css`) - Normalización base
3. **Tipografía** (`_typography.css`) - Estilos de texto
4. **Layout** (`_responsive.css`) - Sistema de grid
5. **Utilidades** (`_utilities.css`) - Clases de ayuda
6. **Componentes** - De simple a complejo
7. **Páginas** - Estilos específicos

## 🎨 Sistema de Variables

### Colores
```css
/* Colores primarios */
--color-primary: #3b82f6;
--color-secondary: #64748b;
--color-accent: #f59e0b;

/* Estados */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #06b6d4;
```

### Espaciado
```css
/* Escala de espaciado (basada en 4px) */
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
```

### Tipografía
```css
/* Familias de fuentes */
--font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Escala tipográfica */
--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-base: 1rem;    /* 16px */
--font-size-lg: 1.125rem;  /* 18px */
--font-size-xl: 1.25rem;   /* 20px */
```

## 📱 Sistema Responsive

### Breakpoints
```css
--breakpoint-sm: 640px;   /* Móviles grandes */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Laptops */
--breakpoint-xl: 1280px;  /* Escritorio */
--breakpoint-2xl: 1536px; /* Pantallas grandes */
```

### Enfoque Mobile-First
```css
/* Base: móvil */
.elemento {
  font-size: var(--font-size-sm);
}

/* Tablet y superior */
@media (min-width: 768px) {
  .elemento {
    font-size: var(--font-size-base);
  }
}
```

## 🧩 Componentes

### Botones
```html
<!-- Botón primario -->
<button class="btn btn--primary">Acción Principal</button>

<!-- Botón secundario -->
<button class="btn btn--secondary">Acción Secundaria</button>

<!-- Botón de contorno -->
<button class="btn btn--outline">Contorno</button>
```

### Formularios
```html
<!-- Grupo de formulario -->
<div class="form-group">
  <label class="form-label" for="input-id">Etiqueta</label>
  <input class="form-input" type="text" id="input-id">
  <span class="form-help">Texto de ayuda</span>
</div>
```

### Tarjetas
```html
<!-- Tarjeta básica -->
<div class="card">
  <div class="card__header">
    <h3 class="card__title">Título</h3>
  </div>
  <div class="card__body">
    <p class="card__text">Contenido de la tarjeta</p>
  </div>
  <div class="card__footer">
    <button class="btn btn--primary">Acción</button>
  </div>
</div>
```

## 🛠️ Utilidades

### Espaciado
```css
/* Márgenes */
.m-0 { margin: 0; }
.m-1 { margin: var(--spacing-1); }
.mt-2 { margin-top: var(--spacing-2); }
.mr-3 { margin-right: var(--spacing-3); }

/* Padding */
.p-0 { padding: 0; }
.p-1 { padding: var(--spacing-1); }
.pt-2 { padding-top: var(--spacing-2); }
.pl-3 { padding-left: var(--spacing-3); }
```

### Display y Layout
```css
.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

.justify-center { justify-content: center; }
.items-center { align-items: center; }
.flex-col { flex-direction: column; }
```

### Responsive
```css
/* Ocultar en móvil */
.hidden-sm { display: none; }
@media (min-width: 768px) {
  .hidden-sm { display: block; }
}

/* Mostrar solo en móvil */
.visible-sm { display: block; }
@media (min-width: 768px) {
  .visible-sm { display: none; }
}
```

## 📝 Nomenclatura (BEM Modificado)

### Estructura
```css
/* Bloque */
.componente { }

/* Elemento */
.componente__elemento { }

/* Modificador */
.componente--modificador { }
.componente__elemento--modificador { }
```

### Ejemplos
```css
/* Botón base */
.btn { }

/* Variantes de botón */
.btn--primary { }
.btn--secondary { }
.btn--large { }

/* Estados */
.btn.is-loading { }
.btn.is-disabled { }
```

## 🎯 Mejores Prácticas

### 1. **Variables CSS**
- Usar variables para valores repetidos
- Nomenclatura semántica y descriptiva
- Agrupar por categorías (colores, espaciado, etc.)

### 2. **Especificidad**
- Mantener baja especificidad
- Evitar `!important` cuando sea posible
- Usar clases en lugar de IDs para estilos

### 3. **Responsive Design**
- Enfoque mobile-first
- Usar breakpoints consistentes
- Probar en múltiples dispositivos

### 4. **Rendimiento**
- Minimizar el CSS en producción
- Usar `will-change` para animaciones
- Optimizar selectores complejos

### 5. **Accesibilidad**
- Mantener contraste adecuado
- Usar unidades relativas
- Respetar preferencias del usuario

## 🔄 Flujo de Desarrollo

### Agregar Nuevos Componentes
1. Crear archivo en `/components/`
2. Definir variables específicas si es necesario
3. Implementar estilos base y variantes
4. Agregar importación en `style.css`
5. Documentar uso y ejemplos

### Agregar Nueva Página
1. Crear archivo en `/pages/`
2. Usar componentes existentes cuando sea posible
3. Definir estilos específicos de la página
4. Agregar importación en `style.css`
5. Probar responsive design

### Modificar Variables
1. Actualizar en `_variables.css`
2. Verificar impacto en componentes
3. Probar en diferentes temas
4. Actualizar documentación si es necesario

## 🧪 Testing y Validación

### Checklist de Calidad
- [ ] CSS válido (W3C Validator)
- [ ] Responsive en todos los breakpoints
- [ ] Accesibilidad (contraste, navegación)
- [ ] Rendimiento (tamaño de archivo)
- [ ] Compatibilidad con navegadores

### Herramientas Recomendadas
- **Validación**: W3C CSS Validator
- **Accesibilidad**: axe DevTools
- **Rendimiento**: Lighthouse
- **Responsive**: Browser DevTools

## 📚 Recursos Adicionales

### Referencias
- [BEM Methodology](http://getbem.com/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)

### Herramientas
- [CSS Variables Generator](https://www.cssportal.com/css-variables-generator/)
- [Color Palette Generator](https://coolors.co/)
- [Typography Scale](https://type-scale.com/)

---

## 📞 Soporte

Para preguntas o sugerencias sobre la arquitectura CSS:

1. Revisar esta documentación
2. Consultar los comentarios en los archivos CSS
3. Verificar ejemplos de uso en los componentes
4. Contactar al equipo de desarrollo frontend

---

**Versión**: 2.0.0  
**Última actualización**: 2024  
**Mantenido por**: Equipo de Desarrollo PACTA