// Funciones para gestión de clientes

// Variables globales
let currentClientId = null;
let isEditMode = false;
let clientesData = [];
let selectedPersonas = [];
let searchTimeout = null;

// Inicialización cuando se carga la página
$(document).ready(function() {
    loadClientes();
    loadEstadisticas();
    initializeEventListeners();
    loadPersonasRecientes();
});

// Configurar event listeners
function initializeEventListeners() {
    // Botón para añadir nuevo cliente
    $('#btnAddClient').on('click', function() {
        openClientModal();
    });
    
    // Botón de búsqueda
    $('#btnSearchClient').on('click', function() {
        toggleSearchBar();
    });
    
    // Event listener para el campo de búsqueda
    $('#searchInput').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        filterClients(searchTerm);
    });
    
    // Event listener para cerrar búsqueda con Escape
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape' && $('#searchContainer').is(':visible')) {
            toggleSearchBar();
        }
    });
    
    // Event listeners para el buscador de personas
    $('#personaSearch').on('input', function() {
        const searchTerm = $(this).val().trim();
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        if (searchTerm.length >= 2) {
            searchTimeout = setTimeout(() => {
                searchPersonas(searchTerm);
            }, 300);
        } else {
            hidePersonaResults();
        }
    });
    
    // Limpiar búsqueda de personas
    $('#clearPersonaSearch').on('click', function() {
        $('#personaSearch').val('');
        hidePersonaResults();
    });
    
    // Limpiar búsqueda general
    $('#clearSearch').on('click', function() {
        $('#searchInput').val('');
        filterClients('');
    });
    
    // Guardar cliente
    $('#saveClientBtn').on('click', function() {
        saveClient();
    });
    
    // Limpiar modal al cerrarse
    $('#clientModal').on('hidden.bs.modal', function() {
        clearClientForm();
    });
}

// Cargar estadísticas
function loadEstadisticas() {
    $.ajax({
        url: '/api/clientes/estadisticas',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                updateMetricCards(response.estadisticas);
            } else {
                console.error('Error al cargar estadísticas:', response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error en la petición de estadísticas:', error);
        }
    });
}

// Actualizar tarjetas de métricas
function updateMetricCards(estadisticas) {
    // Métricas principales
    $('#totalClientes').text(estadisticas.total_clientes || 0);
    $('#clientesActivos').text(estadisticas.clientes_activos || 0);
    $('#clientesInactivos').text(estadisticas.clientes_inactivos || 0);
    $('#nuevosEsteMes').text(estadisticas.nuevos_este_mes || 0);
    
    // Métricas de contratos
    $('#totalContratos').text(estadisticas.contratos_totales || 0);
    $('#contratosActivos').text(estadisticas.contratos_activos || 0);
    $('#valorTotalContratos').text('$' + (estadisticas.valor_total_contratos || 0).toLocaleString());
    
    // Mostrar cambios si están disponibles
    if (estadisticas.cambios) {
        updateChangeIndicators(estadisticas.cambios);
    }
}

// Actualizar indicadores de cambio
function updateChangeIndicators(cambios) {
    const indicators = {
        'cambioTotalClientes': cambios.total_clientes,
        'cambioClientesActivos': cambios.clientes_activos,
        'cambioClientesInactivos': cambios.clientes_inactivos,
        'cambioNuevosEsteMes': cambios.nuevos_este_mes,
        'cambioTotalContratos': cambios.contratos_totales,
        'cambioContratosActivos': cambios.contratos_activos,
        'cambioValorTotalContratos': cambios.valor_total_contratos
    };
    
    Object.keys(indicators).forEach(id => {
        const value = indicators[id];
        const element = $('#' + id);
        
        if (value !== undefined && value !== 0) {
            const isPositive = value > 0;
            const icon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
            const sign = isPositive ? '+' : '';
            
            element.html(`<i class="fas ${icon}"></i> ${sign}${value}%`);
            element.removeClass('text-success text-danger');
            element.addClass(isPositive ? 'text-success' : 'text-danger');
        }
    });
}

// Cargar clientes
function loadClientes() {
    $.ajax({
        url: '/api/clientes',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                clientesData = response.clientes;
                renderClientesTable();
            } else {
                showAlert('Error al cargar clientes: ' + response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            showAlert('Error en la conexión: ' + error, 'error');
        }
    });
}

// Generar avatar para cliente
function generateClientAvatar(nombre, index) {
    const colors = ['blue', 'green', 'purple', 'pink', 'yellow', 'red', 'indigo', 'teal'];
    const colorClass = colors[index % colors.length];
    const initials = nombre.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    
    return `<div class="cliente-avatar color-${colorClass}">${initials}</div>`;
}

// Renderizar tabla de clientes
function renderClientesTable() {
    const tbody = $('#clientesTableBody');
    tbody.empty();
    
    if (clientesData.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center py-4">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay clientes registrados</p>
                </td>
            </tr>
        `);
        return;
    }
    
    const colors = ['blue', 'green', 'purple', 'pink', 'yellow', 'red', 'indigo', 'teal'];
    
    clientesData.forEach((cliente, index) => {
        const colorClass = colors[index % colors.length];
        const iniciales = cliente.nombre.split(' ').map(n => n.charAt(0)).join('').substring(0, 2).toUpperCase();
        
        const estadoBadge = cliente.activo ? 
            '<span class="cliente-badge activo"><i class="fas fa-check-circle"></i> Activo</span>' : 
            '<span class="cliente-badge inactivo"><i class="fas fa-times-circle"></i> Inactivo</span>';
        
        const tipoBadge = `<span class="cliente-badge tipo">${cliente.tipo_cliente || 'N/A'}</span>`;
        
        const fechaRegistro = cliente.fecha_creacion ? 
            new Date(cliente.fecha_creacion).toLocaleDateString() : 'N/A';
        
        const row = `
            <tr>
                <td>
                    <div class="cliente-info">
                        <div class="cliente-avatar color-${colorClass}">
                            ${iniciales}
                        </div>
                        <div class="cliente-details">
                            <p class="cliente-name">${cliente.nombre}</p>
                            <p class="cliente-tipo">${cliente.email || 'Sin email'}</p>
                        </div>
                    </div>
                </td>
                <td>${tipoBadge}</td>
                <td>${cliente.email || 'N/A'}</td>
                <td>${cliente.telefono || 'N/A'}</td>
                <td>${estadoBadge}</td>
                <td>${fechaRegistro}</td>
                <td>
                    <div class="cliente-actions">
                        <button class="cliente-action-btn view" onclick="viewClient(${cliente.id})" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="cliente-action-btn edit" onclick="editClient(${cliente.id})" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="cliente-action-btn ${cliente.activo ? 'warning' : 'success'}" onclick="toggleClientStatus(${cliente.id}, ${!cliente.activo})" title="${cliente.activo ? 'Desactivar' : 'Activar'}">
                            <i class="fas fa-${cliente.activo ? 'pause' : 'play'}"></i>
                        </button>
                        <button class="cliente-action-btn delete" onclick="deleteClient(${cliente.id})" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        
        tbody.append(row);
    });
}

// Obtener badge de tipo
function getTipoBadge(tipo) {
    const tipoMap = {
        'empresa': { text: 'Empresa', class: 'empresa' },
        'persona_fisica': { text: 'Persona Física', class: 'persona-fisica' },
        'gobierno': { text: 'Gobierno', class: 'gobierno' },
        'ong': { text: 'ONG', class: 'ong' },
        'prospecto': { text: 'Prospecto', class: 'prospecto' },
        'cliente': { text: 'Cliente', class: 'cliente' }
    };
    
    const tipoInfo = tipoMap[tipo] || { text: tipo || 'N/A', class: 'default' };
    return `<span class="cliente-badge ${tipoInfo.class}">${tipoInfo.text}</span>`;
}

// Abrir modal de cliente
function openClientModal(clientId = null) {
    currentClientId = clientId;
    isEditMode = clientId !== null;
    
    const modal = new bootstrap.Modal(document.getElementById('clientModal'));
    const modalTitle = $('#clientModalLabel');
    
    if (isEditMode) {
        modalTitle.text('Editar Cliente');
        loadClientData(clientId);
    } else {
        modalTitle.text('Agregar Cliente');
        clearClientForm();
    }
    
    modal.show();
}

// Cargar datos del cliente para edición
function loadClientData(clientId) {
    const cliente = clientesData.find(c => c.id === clientId);
    if (cliente) {
        $('#clientId').val(cliente.id);
        $('#clientName').val(cliente.nombre);
        $('#clientEmail').val(cliente.email);
        $('#clientPhone').val(cliente.telefono);
        $('#clientType').val(cliente.tipo_cliente);
        $('#clientRfc').val(cliente.rfc || '');
        $('#clientSector').val(cliente.sector_industrial || '');
        $('#clientStatus').val(cliente.estado ? 'true' : 'false');
        $('#clientAddress').val(cliente.direccion);
        
        // Cargar personas de contacto si existen
        if (cliente.contacto_principal) {
            loadPersonasForEdit(cliente.contacto_principal);
        }
    }
}

// Guardar cliente
function saveClient() {
    const formData = {
        nombre: $('#clientName').val().trim(),
        email: $('#clientEmail').val().trim(),
        telefono: $('#clientPhone').val().trim(),
        tipo_cliente: $('#clientType').val(),
        rfc: $('#clientRfc').val().trim(),
        sector_industrial: $('#clientSector').val(),
        estado: $('#clientStatus').val() === 'true',
        direccion: $('#clientAddress').val().trim(),
        contacto_principal: selectedPersonas.length > 0 ? JSON.stringify(selectedPersonas.map(p => p.id)) : null
    };
    
    // Validaciones
    if (!formData.nombre) {
        showAlert('El nombre es requerido', 'error');
        return;
    }
    
    if (!formData.email) {
        showAlert('El email es requerido', 'error');
        return;
    }
    
    const url = isEditMode ? `/api/clientes/${currentClientId}` : '/api/clientes';
    const method = isEditMode ? 'PUT' : 'POST';
    
    if (isEditMode) {
        formData.id = currentClientId;
    }
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showAlert(isEditMode ? 'Cliente actualizado exitosamente' : 'Cliente creado exitosamente', 'success');
                bootstrap.Modal.getInstance(document.getElementById('clientModal')).hide();
                loadClientes();
                loadEstadisticas();
            } else {
                showAlert('Error: ' + response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            showAlert('Error en la conexión: ' + error, 'error');
        }
    });
}

// Ver detalles del cliente
function viewClient(clientId) {
    const cliente = clientesData.find(c => c.id === clientId);
    if (!cliente) {
        showAlert('Cliente no encontrado', 'error');
        return;
    }
    
    const content = `
        <div class="row">
            <div class="col-md-6">
                <h6>Información Básica</h6>
                <p><strong>Nombre:</strong> ${cliente.nombre}</p>
                <p><strong>Email:</strong> ${cliente.email || 'N/A'}</p>
                <p><strong>Teléfono:</strong> ${cliente.telefono || 'N/A'}</p>
                <p><strong>Tipo:</strong> ${cliente.tipo_cliente}</p>
                <p><strong>Estado:</strong> ${cliente.activo ? 'Activo' : 'Inactivo'}</p>
            </div>
            <div class="col-md-6">
                <h6>Información Adicional</h6>
                <p><strong>Dirección:</strong> ${cliente.direccion || 'N/A'}</p>
                <p><strong>Fecha de Registro:</strong> ${cliente.fecha_creacion ? new Date(cliente.fecha_creacion).toLocaleDateString() : 'N/A'}</p>
            </div>
        </div>
    `;
    
    $('#viewClientContent').html(content);
    const modal = new bootstrap.Modal(document.getElementById('viewClientModal'));
    modal.show();
}

// Editar cliente
function editClient(clientId) {
    openClientModal(clientId);
}

// Cambiar estado del cliente
function toggleClientStatus(clientId, newStatus) {
    const cliente = clientesData.find(c => c.id === clientId);
    if (!cliente) {
        showAlert('Cliente no encontrado', 'error');
        return;
    }
    
    const action = newStatus ? 'activar' : 'desactivar';
    
    if (confirm(`¿Estás seguro de que deseas ${action} a ${cliente.nombre}?`)) {
        $.ajax({
            url: `/api/clientes/${clientId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({
                id: clientId,
                nombre: cliente.nombre,
                email: cliente.email,
                telefono: cliente.telefono,
                tipo_cliente: cliente.tipo_cliente,
                direccion: cliente.direccion,
                activo: newStatus
            }),
            success: function(response) {
                if (response.success) {
                    showAlert(`Cliente ${action} exitosamente`, 'success');
                    loadClientes();
                    loadEstadisticas();
                } else {
                    showAlert('Error: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showAlert('Error en la conexión: ' + error, 'error');
            }
        });
    }
}

// Eliminar cliente
function deleteClient(clientId) {
    const cliente = clientesData.find(c => c.id === clientId);
    if (!cliente) {
        showAlert('Cliente no encontrado', 'error');
        return;
    }
    
    if (confirm(`¿Estás seguro de que deseas eliminar a ${cliente.nombre}? Esta acción no se puede deshacer.`)) {
        $.ajax({
            url: `/api/clientes/${clientId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    showAlert('Cliente eliminado exitosamente', 'success');
                    loadClientes();
                    loadEstadisticas();
                } else {
                    showAlert('Error: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showAlert('Error en la conexión: ' + error, 'error');
            }
        });
    }
}

// Alternar barra de búsqueda
function toggleSearchBar() {
    const container = $('#searchContainer');
    const input = $('#searchInput');
    
    if (container.is(':visible')) {
        container.slideUp();
        input.val('');
        filterClients('');
    } else {
        container.slideDown();
        input.focus();
    }
}

// Filtrar clientes
function filterClients(searchTerm) {
    const rows = $('#clientesTableBody tr');
    
    if (!searchTerm) {
        rows.show();
        return;
    }
    
    rows.each(function() {
        const row = $(this);
        const text = row.text().toLowerCase();
        
        if (text.includes(searchTerm)) {
            row.show();
        } else {
            row.hide();
        }
    });
}

// Buscar personas
function searchPersonas(searchTerm) {
    $.ajax({
        url: '/api/personas/search',
        method: 'GET',
        data: { q: searchTerm },
        success: function(response) {
            if (response.success) {
                displayPersonaResults(response.personas);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error buscando personas:', error);
        }
    });
}

// Mostrar resultados de búsqueda de personas
function displayPersonaResults(personas) {
    const container = $('#personaResults');
    container.empty();
    
    if (personas.length === 0) {
        container.append('<div class="list-group-item text-muted">No se encontraron personas</div>');
    } else {
        personas.forEach(persona => {
            const item = `
                <div class="list-group-item list-group-item-action" onclick="selectPersona(${JSON.stringify(persona).replace(/"/g, '&quot;')})">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${persona.nombre} ${persona.apellido || ''}</h6>
                            <small class="text-muted">${persona.email || 'Sin email'}</small>
                        </div>
                        <small>${persona.cargo || 'Sin cargo'}</small>
                    </div>
                </div>
            `;
            container.append(item);
        });
    }
    
    container.show();
}

// Seleccionar persona
function selectPersona(persona) {
    // Verificar si ya está seleccionada
    if (selectedPersonas.find(p => p.id === persona.id)) {
        showAlert('Esta persona ya está seleccionada', 'warning');
        return;
    }
    
    selectedPersonas.push(persona);
    updateSelectedPersonasDisplay();
    hidePersonaResults();
    $('#personaSearch').val('');
}

// Actualizar display de personas seleccionadas
function updateSelectedPersonasDisplay() {
    const container = $('#selectedPersonas');
    container.empty();
    
    selectedPersonas.forEach((persona, index) => {
        const badge = `
            <span class="badge bg-primary me-2 mb-2">
                ${persona.nombre} ${persona.apellido || ''}
                <button type="button" class="btn-close btn-close-white ms-2" onclick="removePersona(${index})" aria-label="Remove"></button>
            </span>
        `;
        container.append(badge);
    });
}

// Remover persona
function removePersona(index) {
    selectedPersonas.splice(index, 1);
    updateSelectedPersonasDisplay();
}

// Ocultar resultados de personas
function hidePersonaResults() {
    $('#personaResults').hide();
}

// Cargar personas para edición
function loadPersonasForEdit(contactoPrincipal) {
    try {
        let personaIds = [];
        
        if (typeof contactoPrincipal === 'string') {
            if (contactoPrincipal.startsWith('[') || contactoPrincipal.startsWith('{')) {
                const parsed = JSON.parse(contactoPrincipal);
                if (Array.isArray(parsed)) {
                    personaIds = parsed;
                } else if (typeof parsed === 'object') {
                    personaIds = Object.values(parsed);
                }
            } else {
                personaIds = [parseInt(contactoPrincipal)];
            }
        } else if (Array.isArray(contactoPrincipal)) {
            personaIds = contactoPrincipal;
        }
        
        if (personaIds.length > 0) {
            $.ajax({
                url: '/api/personas/by-ids',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ ids: personaIds }),
                success: function(response) {
                    if (response.success) {
                        selectedPersonas = response.personas;
                        updateSelectedPersonasDisplay();
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error cargando personas:', error);
                }
            });
        }
    } catch (error) {
        console.error('Error procesando contacto principal:', error);
    }
}

// Limpiar formulario
function clearClientForm() {
    $('#clientForm')[0].reset();
    $('#clientId').val('');
    selectedPersonas = [];
    updateSelectedPersonasDisplay();
    hidePersonaResults();
    currentClientId = null;
    isEditMode = false;
}

// Mostrar alerta
function showAlert(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alert = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Remover alertas existentes
    $('.alert').remove();
    
    // Agregar nueva alerta al inicio del contenido
    $('.content').prepend(alert);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        $('.alert').fadeOut();
    }, 5000);
}

// Cargar personas recientes
function loadPersonasRecientes() {
    $.ajax({
        url: '/api/clientes/personas-recientes',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                renderPersonasRecientes(response.personas);
            } else {
                showPersonasError('Error al cargar personas recientes');
            }
        },
        error: function(xhr, status, error) {
            showPersonasError('Error en la conexión');
        }
    });
}

// Renderizar personas recientes
function renderPersonasRecientes(personas) {
    const container = $('#personasRecientesContainer');
    container.empty();
    
    if (personas.length === 0) {
        container.append(`
            <div class="col-12">
                <div class="text-center py-4">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay personas responsables registradas</p>
                </div>
            </div>
        `);
        return;
    }
    
    personas.forEach((persona, index) => {
        const avatar = generatePersonaAvatar(persona.nombre, index);
        const clienteInfo = persona.cliente_nombre ? 
            `<small class="text-muted">Cliente: ${persona.cliente_nombre}</small>` : 
            '<small class="text-muted">Sin cliente asignado</small>';
        
        const card = `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            ${avatar}
                            <div class="ms-3">
                                <h6 class="card-title mb-1">${persona.nombre} ${persona.apellido || ''}</h6>
                                ${clienteInfo}
                            </div>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted"><i class="fas fa-envelope me-1"></i> ${persona.email || 'Sin email'}</small>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted"><i class="fas fa-phone me-1"></i> ${persona.telefono || 'Sin teléfono'}</small>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted"><i class="fas fa-briefcase me-1"></i> ${persona.cargo || 'Sin cargo'}</small>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                ${persona.fecha_creacion ? new Date(persona.fecha_creacion).toLocaleDateString() : 'Fecha N/A'}
                            </small>
                            <button class="btn btn-sm btn-outline-primary" onclick="viewPersonaDetails(${persona.id})">
                                <i class="fas fa-eye"></i> Ver
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.append(card);
    });
}

// Generar avatar para persona
function generatePersonaAvatar(nombre, index) {
    const colors = [
        '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1',
        '#fd7e14', '#20c997', '#e83e8c', '#6610f2', '#6f42c1', '#e83e8c'
    ];
    const color = colors[index % colors.length];
    const initials = nombre.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    
    return `
        <div class="avatar" style="
            background-color: ${color}; 
            color: white; 
            width: 45px; 
            height: 45px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: bold;
            font-size: 16px;
        ">${initials}</div>
    `;
}

// Mostrar error en sección de personas
function showPersonasError(message) {
    const container = $('#personasRecientesContainer');
    container.html(`
        <div class="col-12">
            <div class="alert alert-warning" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        </div>
    `);
}

// Ver detalles de persona
function viewPersonaDetails(personaId) {
    $.ajax({
        url: `/api/personas/${personaId}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                showPersonaDetailsModal(response.persona);
            } else {
                showAlert('Error al cargar detalles de la persona', 'error');
            }
        },
        error: function(xhr, status, error) {
            showAlert('Error en la conexión', 'error');
        }
    });
}

// Mostrar modal de detalles de persona
function showPersonaDetailsModal(persona) {
    const content = `
        <div class="row">
            <div class="col-12">
                <div class="d-flex align-items-center mb-3">
                    ${generatePersonaAvatar(persona.nombre, 0)}
                    <div class="ms-3">
                        <h5 class="mb-1">${persona.nombre} ${persona.apellido || ''}</h5>
                        <p class="text-muted mb-0">${persona.cargo || 'Sin cargo especificado'}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <h6>Información de Contacto</h6>
                <p><strong>Email:</strong> ${persona.email || 'N/A'}</p>
                <p><strong>Teléfono:</strong> ${persona.telefono || 'N/A'}</p>
            </div>
            <div class="col-md-6">
                <h6>Información Adicional</h6>
                <p><strong>Fecha de Registro:</strong> ${persona.fecha_creacion ? new Date(persona.fecha_creacion).toLocaleDateString() : 'N/A'}</p>
                <p><strong>Estado:</strong> ${persona.activo ? 'Activo' : 'Inactivo'}</p>
            </div>
        </div>
    `;
    
    $('#personaDetailsContent').html(content);
    const modal = new bootstrap.Modal(document.getElementById('personaDetailsModal'));
    modal.show();
}