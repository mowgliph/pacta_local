/**
 * Funciones para manejo de contratos y gráficos
 */

/**
 * Configuración responsiva para gráficos
 */
function getChartSize() {
    return window.innerWidth <= 480 ? 100 : 120;
}

function updateChartSize() {
    const size = getChartSize();
    const statusCanvas = document.getElementById('statusChart');
    const typeCanvas = document.getElementById('typeChart');
    
    if (statusCanvas && typeCanvas) {
        statusCanvas.width = size;
        statusCanvas.height = size;
        typeCanvas.width = size;
        typeCanvas.height = size;
    }
}

/**
 * Inicializa los gráficos de contratos
 */
function initializeContractCharts() {
    // Status Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusChart = new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [89, 11],
                    backgroundColor: ['#10b981', '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%',
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
        
        // Guardar referencia para redimensionamiento
        window.statusChart = statusChart;
    }
    
    // Type Chart
    const typeCtx = document.getElementById('typeChart');
    if (typeCtx) {
        const typeChart = new Chart(typeCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [65, 35],
                    backgroundColor: ['#3b82f6', '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%',
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
        
        // Guardar referencia para redimensionamiento
        window.typeChart = typeChart;
    }
    
    // Configurar eventos de redimensionamiento
    window.addEventListener('resize', function() {
        updateChartSize();
        if (window.statusChart) window.statusChart.resize();
        if (window.typeChart) window.typeChart.resize();
    });
    
    // Actualización inicial del tamaño
    updateChartSize();
}

/**
 * Crear un nuevo contrato (función de ejemplo para futuras implementaciones)
 */
function createNewContract() {
    // Implementar lógica para crear nuevo contrato
    console.log('Creando nuevo contrato...');
    // Esta función se puede expandir para abrir un modal de creación
}

/**
 * Editar un contrato existente
 * @param {number} contractId - ID del contrato a editar
 */
function editContract(contractId) {
    // Implementar lógica para editar contrato
    console.log('Editando contrato:', contractId);
    // Esta función se puede expandir para abrir un modal de edición
}

/**
 * Eliminar un contrato
 * @param {number} contractId - ID del contrato a eliminar
 */
function deleteContract(contractId) {
    if (confirm('¿Está seguro de que desea eliminar este contrato?')) {
        fetch(`/eliminar_contrato/${contractId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Contrato eliminado exitosamente');
                window.location.reload();
            } else {
                alert('Error al eliminar contrato: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar contrato');
        });
    }
}

/**
 * Renovar un contrato
 * @param {number} contractId - ID del contrato a renovar
 */
function renewContract(contractId) {
    if (confirm('¿Está seguro de que desea renovar este contrato?')) {
        fetch(`/renovar_contrato/${contractId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Contrato renovado exitosamente');
                window.location.reload();
            } else {
                alert('Error al renovar contrato: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al renovar contrato');
        });
    }
}

/**
 * Filtrar contratos por estado
 * @param {string} status - Estado del contrato (activo, vencido, etc.)
 */
function filterContractsByStatus(status) {
    // Implementar lógica de filtrado
    console.log('Filtrando contratos por estado:', status);
    // Esta función se puede expandir para filtrar la tabla de contratos
}

/**
 * Buscar contratos por texto
 * @param {string} searchTerm - Término de búsqueda
 */
function searchContracts(searchTerm) {
    // Implementar lógica de búsqueda
    console.log('Buscando contratos:', searchTerm);
    // Esta función se puede expandir para buscar en la tabla de contratos
}

// Inicializar gráficos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en la página de contratos
    if (document.getElementById('statusChart') || document.getElementById('typeChart')) {
        initializeContractCharts();
    }
});