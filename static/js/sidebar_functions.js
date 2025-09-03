// Funciones para el manejo del sidebar

// Función para manejar la navegación activa en el sidebar
function initializeSidebarNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;
    
    // Remover clase active de todos los elementos
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Añadir clase active al elemento correspondiente basado en la URL actual
    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link) {
            const href = link.getAttribute('href');
            
            // Verificar si la URL actual coincide con el href del enlace
            if (currentPath === href || 
                (currentPath === '/' && href.includes('dashboard')) ||
                (currentPath.includes('contratos') && href.includes('contratos')) ||
                (currentPath.includes('suplementos') && href.includes('suplementos')) ||
                (currentPath.includes('reportes') && href.includes('reportes')) ||
                (currentPath.includes('usuario') && href.includes('usuario')) ||
                (currentPath.includes('configuracion') && href.includes('configuracion'))) {
                item.classList.add('active');
            }
        }
    });
    
    // Añadir event listeners para clicks en los enlaces
    navItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link) {
            link.addEventListener('click', function(e) {
                // Remover active de todos los elementos
                navItems.forEach(navItem => {
                    navItem.classList.remove('active');
                });
                
                // Añadir active al elemento clickeado
                item.classList.add('active');
            });
        }
    });
}

// Función para colapsar/expandir sidebar en móviles
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// Función para cerrar sidebar en móviles al hacer click fuera
function closeSidebarOnOutsideClick(event) {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    
    if (sidebar && !sidebar.contains(event.target) && !sidebarToggle?.contains(event.target)) {
        sidebar.classList.remove('show');
    }
}

// Inicializar funciones del sidebar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebarNavigation();
    
    // Añadir listener para clicks fuera del sidebar
    document.addEventListener('click', closeSidebarOnOutsideClick);
});