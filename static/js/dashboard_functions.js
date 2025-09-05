// Dashboard Functions - Gestión de gráficos y funcionalidades del dashboard

// Configuración responsiva de gráficos
function getChartSize() {
    return window.innerWidth <= 480 ? 100 : 120;
}

function updateChartSize() {
    const size = getChartSize();
    const contractsCanvas = document.getElementById('contractsOverviewChart');
    const reportsCanvas = document.getElementById('reportsOverviewChart');
    
    if (contractsCanvas && reportsCanvas) {
        contractsCanvas.width = size;
        contractsCanvas.height = size;
        reportsCanvas.width = size;
        reportsCanvas.height = size;
    }
}

// Inicialización de gráficos del dashboard
function initializeDashboardCharts(estadisticas) {
    // Validar que las estadísticas sean válidas
    if (!estadisticas || typeof estadisticas !== 'object') {
        console.error('Estadísticas no válidas para inicializar gráficos');
        return;
    }
    
    // Gráfico de Contratos
    const contractsCtx = document.getElementById('contractsOverviewChart');
    if (contractsCtx) {
        try {
            // Validar datos numéricos
            const contratosActivos = Number(estadisticas.contratos_activos) || 0;
            const contratosPorVencer = Number(estadisticas.contratos_por_vencer) || 0;
            const totalContratos = Number(estadisticas.total_contratos) || 0;
            const contratosVencidos = Math.max(0, totalContratos - contratosActivos - contratosPorVencer);
            
            const contractsChart = new Chart(contractsCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [contratosActivos, contratosPorVencer, contratosVencidos],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    cutout: '70%'
                }
            });
        } catch (error) {
            console.error('Error al crear gráfico de contratos:', error);
        }
    } else {
        console.warn('Elemento contractsOverviewChart no encontrado');
    }
    
    // Gráfico de Reportes
    const reportsCtx = document.getElementById('reportsOverviewChart');
    if (reportsCtx) {
        try {
            // Validar datos numéricos
            const reportesMes = Number(estadisticas.reportes_mes) || 0;
            const totalReportes = Number(estadisticas.total_reportes) || 0;
            const reportesAnteriores = Math.max(0, totalReportes - reportesMes);
            
            const reportsChart = new Chart(reportsCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [reportesMes, reportesAnteriores],
                        backgroundColor: ['#3b82f6', '#e5e7eb'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    cutout: '70%'
                }
            });
        } catch (error) {
            console.error('Error al crear gráfico de reportes:', error);
        }
    } else {
        console.warn('Elemento reportsOverviewChart no encontrado');
    }
}

// Event listeners para el dashboard
function initializeDashboardEvents() {
    // Actualizar tamaños de gráficos en redimensionamiento
    window.addEventListener('resize', function() {
        updateChartSize();
    });
    
    // Inicializar tamaños de gráficos
    updateChartSize();
}

// Función principal de inicialización del dashboard
function initializeDashboard(estadisticas) {
    try {
        // Validar que Chart.js esté disponible
        if (typeof Chart === 'undefined') {
            console.error('Chart.js no está disponible. No se pueden inicializar los gráficos.');
            return false;
        }
        
        // Validar estadísticas
        if (!estadisticas) {
            console.error('No se proporcionaron estadísticas para el dashboard.');
            return false;
        }
        
        console.log('Inicializando dashboard con estadísticas:', estadisticas);
        
        // Inicializar gráficos
        initializeDashboardCharts(estadisticas);
        
        // Inicializar eventos
        initializeDashboardEvents();
        
        console.log('Dashboard inicializado correctamente');
        return true;
    } catch (error) {
        console.error('Error en la inicialización del dashboard:', error);
        return false;
    }
}

// Exportar funciones para uso global
window.dashboardFunctions = {
    initialize: initializeDashboard,
    updateChartSize: updateChartSize,
    getChartSize: getChartSize
};