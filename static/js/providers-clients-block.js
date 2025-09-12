/**
 * Funciones JavaScript para el componente providers-clients-block
 * Maneja la carga de datos dinámicos y la funcionalidad del bloque
 */

class ProvidersClientsBlock {
    constructor(containerId, config = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.config = {
            providersApiUrl: config.providersApiUrl || '/api/providers-summary',
            clientsApiUrl: config.clientsApiUrl || '/api/clients-summary',
            showProviders: config.showProviders !== false,
            showClients: config.showClients !== false,
            maxItems: config.maxItems || 3,
            ...config
        };
        
        if (!this.container) {
            console.error(`Container with ID '${containerId}' not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        this.loadData();
    }
    
    async loadData() {
        try {
            this.showLoading();
            
            // Fetch both providers and clients data separately
            const [providersResponse, clientsResponse] = await Promise.all([
                fetch(this.config.providersApiUrl, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }),
                fetch(this.config.clientsApiUrl, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
            ]);
            
            // Check for authentication errors
            if (!providersResponse.ok || !clientsResponse.ok) {
                if (providersResponse.status === 401 || clientsResponse.status === 401) {
                    this.showError('Sesión expirada. Por favor, inicia sesión nuevamente.');
                    return;
                }
                throw new Error(`HTTP error! Providers: ${providersResponse.status}, Clients: ${clientsResponse.status}`);
            }
            
            const providersData = await providersResponse.json();
            const clientsData = await clientsResponse.json();
            
            // Check for API-level errors
            if (!providersData.success && providersData.redirect) {
                this.showError('Sesión expirada. Por favor, inicia sesión nuevamente.');
                return;
            }
            if (!clientsData.success && clientsData.redirect) {
                this.showError('Sesión expirada. Por favor, inicia sesión nuevamente.');
                return;
            }
            
            // Combine the data
            const combinedData = {
                success: true,
                providers: providersData.success ? providersData.providers : [],
                clients: clientsData.success ? clientsData.clients : []
            };
            
            this.renderData(combinedData);
        } catch (error) {
            console.error('Error loading providers-clients data:', error);
            this.showError('Error de conexión al cargar los datos');
        }
    }
    
    showLoading() {
        const loadingElement = this.container.querySelector('.loading-state');
        const errorElement = this.container.querySelector('.error-state');
        const contentElement = this.container.querySelector('.providers-clients-content');
        
        if (loadingElement) loadingElement.style.display = 'block';
        if (errorElement) errorElement.style.display = 'none';
        if (contentElement) contentElement.style.display = 'none';
    }
    
    showError(message) {
        const loadingElement = this.container.querySelector('.loading-state');
        const errorElement = this.container.querySelector('.error-state');
        const contentElement = this.container.querySelector('.providers-clients-content');
        
        if (loadingElement) loadingElement.style.display = 'none';
        if (errorElement) {
            errorElement.style.display = 'block';
            const errorMessage = errorElement.querySelector('.error-message');
            if (errorMessage) errorMessage.textContent = message;
        }
        if (contentElement) contentElement.style.display = 'none';
    }
    
    renderData(data) {
        const loadingElement = this.container.querySelector('.loading-state');
        const errorElement = this.container.querySelector('.error-state');
        const contentElement = this.container.querySelector('.providers-clients-content');
        
        if (loadingElement) loadingElement.style.display = 'none';
        if (errorElement) errorElement.style.display = 'none';
        if (contentElement) contentElement.style.display = 'block';
        
        // Renderizar proveedores
        if (this.config.showProviders && data.providers) {
            this.renderProviders(data.providers);
        }
        
        // Renderizar clientes
        if (this.config.showClients && data.clients) {
            this.renderClients(data.clients);
        }
    }
    
    renderProviders(providers) {
        const providersContainer = this.container.querySelector(`#${this.containerId}-providers-list`);
        if (!providersContainer) {
            console.error(`Providers container not found: #${this.containerId}-providers-list`);
            return;
        }
        
        providersContainer.innerHTML = '';
        
        if (providers.length === 0) {
            providersContainer.innerHTML = '<p class="text-muted">No hay proveedores disponibles</p>';
            return;
        }
        
        providers.slice(0, this.config.maxItems).forEach(provider => {
            const providerCard = this.createProviderCard(provider);
            providersContainer.appendChild(providerCard);
        });
    }
    
    renderClients(clients) {
        const clientsContainer = this.container.querySelector(`#${this.containerId}-clients-list`);
        if (!clientsContainer) {
            console.error(`Clients container not found: #${this.containerId}-clients-list`);
            return;
        }
        
        clientsContainer.innerHTML = '';
        
        if (clients.length === 0) {
            clientsContainer.innerHTML = '<p class="text-muted">No hay clientes disponibles</p>';
            return;
        }
        
        clients.slice(0, this.config.maxItems).forEach(client => {
            const clientCard = this.createClientCard(client);
            clientsContainer.appendChild(clientCard);
        });
    }
    
    createProviderCard(provider) {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-3';
        
        const formattedValue = this.formatCurrency(provider.total_value);
        
        card.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title text-truncate" title="${provider.nombre}">${provider.nombre}</h6>
                    <p class="card-text small text-muted mb-2">${provider.industria}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${provider.contratos_count} contrato(s)</small>
                        <small class="text-success font-weight-bold">${formattedValue}</small>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    createClientCard(client) {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-3';
        
        const formattedValue = this.formatCurrency(client.total_value);
        
        card.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title text-truncate" title="${client.nombre}">${client.nombre}</h6>
                    <p class="card-text small text-muted mb-2">${client.sector}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${client.contratos_count} contrato(s)</small>
                        <small class="text-success font-weight-bold">${formattedValue}</small>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    formatCurrency(amount) {
        if (!amount || amount === 0) return '$0';
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }
    
    refresh() {
        this.loadData();
    }
}

// Función global para inicializar el componente
function initProvidersClientsBlock(containerId, config = {}) {
    return new ProvidersClientsBlock(containerId, config);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize providers-clients blocks
    const providersClientsMain = document.getElementById('providers-clients-main');
    if (providersClientsMain) {
        const config = {
            providersApiUrl: '/api/providers-summary',
            clientsApiUrl: '/api/clients-summary',
            showProviders: true,
            showClients: true,
            maxItems: 3
        };
        const block = new ProvidersClientsBlock('providers-clients-main', config);
        block.init();
    }
    
    const providersClientsContratos = document.getElementById('providers-clients-contratos');
    if (providersClientsContratos) {
        const config = {
            providersApiUrl: '/api/providers-summary',
            clientsApiUrl: '/api/clients-summary',
            showProviders: true,
            showClients: true,
            maxItems: 3
        };
        const block = new ProvidersClientsBlock('providers-clients-contratos', config);
        block.init();
    }
});

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProvidersClientsBlock, initProvidersClientsBlock };
}