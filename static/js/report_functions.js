// Funciones para el manejo de reportes

// Configuración de gráficos responsivos
function getChartSize() {
    return window.innerWidth < 768 ? { width: 120, height: 120 } : { width: 140, height: 140 };
}

function updateChartSize() {
    const size = getChartSize();
    // Actualizar tamaños de gráficos si es necesario
}

// Inicialización de gráficos de reportes
function initializeReportCharts() {
    // Type Distribution Chart
    const typeCtx = document.getElementById('typeDistChart');
    if (typeCtx) {
        new Chart(typeCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [67, 33],
                    backgroundColor: ['#3b82f6', '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%'
            }
        });
    }

    // Status Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [94, 6],
                    backgroundColor: ['#10b981', '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%'
            }
        });
    }
}

// Funciones para el manejo de reportes
function generateReport(type) {
    console.log('Generando reporte:', type);
    // Implementar lógica para generar reportes
}

function downloadReport(reportId) {
    console.log('Descargando reporte:', reportId);
    // Implementar lógica para descargar reportes
}

function viewReport(reportId) {
    console.log('Visualizando reporte:', reportId);
    // Implementar lógica para visualizar reportes
}

function scheduleReport(reportData) {
    console.log('Programando reporte:', reportData);
    // Implementar lógica para programar reportes
}

function deleteReport(reportId) {
    if (confirm('¿Estás seguro de que deseas eliminar este reporte?')) {
        console.log('Eliminando reporte:', reportId);
        // Implementar lógica para eliminar reportes
    }
}

function filterReports(criteria) {
    console.log('Filtrando reportes:', criteria);
    // Implementar lógica para filtrar reportes
}

function searchReports(query) {
    console.log('Buscando reportes:', query);
    // Implementar lógica para buscar reportes
}

function exportReportData(format) {
    console.log('Exportando datos en formato:', format);
    // Implementar lógica para exportar datos
}

// Inicializar gráficos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeReportCharts();
});

// Manejar redimensionamiento de ventana
window.addEventListener('resize', updateChartSize);