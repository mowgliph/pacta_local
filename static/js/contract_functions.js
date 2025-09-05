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
    // Abrir el modal de crear contrato
    const modal = new bootstrap.Modal(document.getElementById('crearContratoModal'));
    modal.show();
    
    // Generar número de contrato automáticamente
    const numeroContrato = document.getElementById('numero_contrato');
    if (numeroContrato && !numeroContrato.value) {
        const fecha = new Date();
        const año = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, '0');
        const dia = String(fecha.getDate()).padStart(2, '0');
        const hora = String(fecha.getHours()).padStart(2, '0');
        const minuto = String(fecha.getMinutes()).padStart(2, '0');
        numeroContrato.value = `CONT-${año}${mes}${dia}-${hora}${minuto}`;
    }
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

/**
 * Variables globales para la búsqueda avanzada
 */
let currentFilter = 'all';
let currentSearchTerm = '';

/**
 * Inicializar la búsqueda avanzada de contratos
 */
function initializeAdvancedSearch() {
    const searchInput = document.getElementById('contractSearchInput');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const applySearchBtn = document.getElementById('applySearch');
    const clearSearchBtn = document.getElementById('clearSearch');

    if (!searchInput || !filterButtons.length) return;

    // Manejar cambios en los filtros
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover clase active de todos los botones
            filterButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = 'white';
                btn.style.color = '#374151';
            });
            
            // Agregar clase active al botón seleccionado
            this.classList.add('active');
            this.style.background = '#3b82f6';
            this.style.color = 'white';
            
            currentFilter = this.getAttribute('data-filter');
            console.log('Filtro seleccionado:', currentFilter);
        });
    });

    // Manejar búsqueda en tiempo real
    searchInput.addEventListener('input', function() {
        currentSearchTerm = this.value.trim();
    });

    // Manejar búsqueda con Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyAdvancedSearch();
        }
    });

    // Botón aplicar búsqueda
    if (applySearchBtn) {
        applySearchBtn.addEventListener('click', applyAdvancedSearch);
    }

    // Botón limpiar búsqueda
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', clearAdvancedSearch);
    }
}

/**
 * Aplicar búsqueda avanzada con filtros
 */
function applyAdvancedSearch() {
    console.log('Aplicando búsqueda avanzada:');
    console.log('- Término de búsqueda:', currentSearchTerm);
    console.log('- Filtro por tipo:', currentFilter);
    
    // Aquí se implementaría la lógica para filtrar los contratos
    // Por ejemplo, hacer una petición AJAX al servidor con los parámetros
    
    const searchParams = {
        search: currentSearchTerm,
        filter: currentFilter
    };
    
    // Ejemplo de petición AJAX (comentado para evitar errores)
    /*
    fetch('/api/contratos/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams)
    })
    .then(response => response.json())
    .then(data => {
        updateContractsTable(data.contratos);
    })
    .catch(error => {
        console.error('Error en la búsqueda:', error);
    });
    */
    
    // Mostrar mensaje temporal
    showSearchMessage(`Buscando contratos con filtro "${currentFilter}" y término "${currentSearchTerm}"`);
}

/**
 * Limpiar búsqueda avanzada
 */
function clearAdvancedSearch() {
    const searchInput = document.getElementById('contractSearchInput');
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    // Limpiar input de búsqueda
    if (searchInput) {
        searchInput.value = '';
        currentSearchTerm = '';
    }
    
    // Resetear filtros al "Todos"
    filterButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.style.background = 'white';
        btn.style.color = '#374151';
    });
    
    const allButton = document.getElementById('filterAll');
    if (allButton) {
        allButton.classList.add('active');
        allButton.style.background = '#3b82f6';
        allButton.style.color = 'white';
    }
    
    currentFilter = 'all';
    
    console.log('Búsqueda limpiada');
    showSearchMessage('Búsqueda limpiada - Mostrando todos los contratos');
}

/**
 * Mostrar mensaje de búsqueda temporal
 */
function showSearchMessage(message) {
    // Crear o actualizar mensaje temporal
    let messageDiv = document.getElementById('searchMessage');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'searchMessage';
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            font-size: 14px;
            max-width: 300px;
        `;
        document.body.appendChild(messageDiv);
    }
    
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        if (messageDiv) {
            messageDiv.style.display = 'none';
        }
    }, 3000);
}

// Inicializar gráficos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en la página de contratos
    if (document.getElementById('statusChart') || document.getElementById('typeChart')) {
        initializeContractCharts();
    }
    
    // Inicializar búsqueda avanzada
    if (document.getElementById('contractSearchInput')) {
        initializeAdvancedSearch();
    }
});