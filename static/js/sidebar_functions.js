// Funciones para el manejo del sidebar

// Función para manejar la navegación activa en el sidebar (BEM)
function initializeSidebarNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav__link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        link.classList.remove('sidebar-nav__link--active');
        const href = link.getAttribute('href') || '';
        if (
            currentPath === href ||
            (currentPath === '/' && href.includes('dashboard')) ||
            (currentPath.includes('contratos') && href.includes('contratos')) ||
            (currentPath.includes('suplementos') && href.includes('suplementos')) ||
            (currentPath.includes('reportes') && href.includes('reportes')) ||
            (currentPath.includes('usuario') && href.includes('usuario')) ||
            (currentPath.includes('configuracion') && href.includes('configuracion'))
        ) {
            link.classList.add('sidebar-nav__link--active');
        }
    });

    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('sidebar-nav__link--active'));
            this.classList.add('sidebar-nav__link--active');
        });
    });
}

// Toggle sidebar en móviles (abre/cierra)
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.toggle('sidebar--open');
    overlay.classList.toggle('sidebar-overlay--visible', isOpen);
}

// Cerrar sidebar al click fuera o sobre overlay
function closeSidebarOnOutsideClick(event) {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (!sidebar || !overlay) return;

    const clickedOutside = !sidebar.contains(event.target) && !toggleBtn?.contains(event.target);
    const clickedOverlay = overlay.contains(event.target);

    if (sidebar.classList.contains('sidebar--open') && (clickedOutside || clickedOverlay)) {
        sidebar.classList.remove('sidebar--open');
        overlay.classList.remove('sidebar-overlay--visible');
    }
}

// Inicializar funciones del sidebar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebarNavigation();

    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    }

    // Añadir listener para clicks fuera del sidebar y sobre overlay
    document.addEventListener('click', closeSidebarOnOutsideClick);
});