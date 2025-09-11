// Funciones para gestión de proveedores

// Variables globales
let currentProviderId = null;
let isEditMode = false;
let proveedoresData = [];
let selectedPersonas = [];
let searchTimeout = null;

// Inicialización cuando se carga la página
$(document).ready(function() {
    loadProveedores();
    loadEstadisticas();
    initializeEventListeners();
    

});



// Configurar event listeners
function initializeEventListeners() {
    // Botón para añadir nuevo proveedor
    $('#btnAddProvider').on('click', function() {
        openProviderModal();
    });
    
    // Botón de búsqueda
    $('#btnSearchProvider').on('click', function() {
        toggleSearchBar();
    });
    
    // Event listener para el campo de búsqueda
    $('#searchInput').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        filterProviders(searchTerm);
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
            $('#personaSearchResults').hide().removeClass('show');
        }
    });
    
    // Ocultar resultados al hacer clic fuera
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#personaSearch, #personaSearchResults').length) {
            $('#personaSearchResults').hide().removeClass('show');
        }
    });
    
    // Botón guardar en modal
    $('#saveProviderBtn').on('click', function() {
        saveProvider();
    });
    
    // Botones de acción en la tabla
    $(document).on('click', '.btn-view-provider', function() {
        const providerId = $(this).data('id');
        viewProvider(providerId);
    });
    
    $(document).on('click', '.btn-edit-provider', function() {
        const providerId = $(this).data('id');
        editProvider(providerId);
    });
    
    $(document).on('click', '.btn-toggle-provider', function() {
        const providerId = $(this).data('id');
        toggleProviderStatus(providerId);
    });
    
    $(document).on('click', '.btn-delete-provider', function() {
        const providerId = $(this).data('id');
        deleteProvider(providerId);
    });
}

// Cargar estadísticas de proveedores
function loadEstadisticas() {
    $.ajax({
        url: '/api/proveedores/estadisticas',
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

// Actualizar las tarjetas métricas con datos dinámicos
function updateMetricCards(estadisticas) {
    // Actualizar Total Proveedores
    $('.metrics-grid .metric-card').eq(0).find('.metric-value').text(estadisticas.total_proveedores);
    const cambioProveedores = estadisticas.cambio_proveedores || 0;
    const textoProveedores = cambioProveedores >= 0 ? `+${cambioProveedores} este mes` : `${cambioProveedores} este mes`;
    $('.metrics-grid .metric-card').eq(0).find('.metric-change').text(textoProveedores);
    
    // Actualizar Proveedores Activos
    $('.metrics-grid .metric-card').eq(1).find('.metric-value').text(estadisticas.proveedores_activos);
    const porcentajeActivos = estadisticas.porcentaje_activos || 0;
    $('.metrics-grid .metric-card').eq(1).find('.metric-change').text(porcentajeActivos + '% del total');
    
    // Actualizar Contratos Totales
    $('.metrics-grid .metric-card').eq(2).find('.metric-value').text(estadisticas.contratos_totales);
    const cambioContratos = estadisticas.cambio_contratos || 0;
    const textoContratos = cambioContratos >= 0 ? `+${cambioContratos} este mes` : `${cambioContratos} este mes`;
    $('.metrics-grid .metric-card').eq(2).find('.metric-change').text(textoContratos);
    
    // Actualizar Valor Promedio
    const valorPromedio = new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 0
    }).format(estadisticas.valor_promedio);
    $('.metrics-grid .metric-card').eq(3).find('.metric-value').text(valorPromedio);
    $('.metrics-grid .metric-card').eq(3).find('.metric-change').text('Por contrato');
}

// Cargar lista de proveedores
function loadProveedores() {
    $.ajax({
        url: '/api/proveedores',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                proveedoresData = response.proveedores;
                renderProveedoresTable();
            } else {
                showAlert('Error al cargar proveedores: ' + response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            showAlert('Error de conexión al cargar proveedores', 'error');
        }
    });
}

// Función para generar avatar de proveedor
function generateProveedorAvatar(nombre, index) {
    const colors = [
        'color-blue', 'color-green', 'color-purple', 'color-pink',
        'color-yellow', 'color-red', 'color-indigo', 'color-teal'
    ];
    
    const colorClass = colors[index % colors.length];
    const initials = nombre.split(' ').map(word => word.charAt(0)).join('').substring(0, 2);
    
    return `<div class="proveedor-avatar ${colorClass}">${initials}</div>`;
}

// Renderizar tabla de proveedores
function renderProveedoresTable() {
    const tbody = $('#providersTableBody');
    tbody.empty();
    
    if (proveedoresData.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                    No se encontraron proveedores
                </td>
            </tr>
        `);
        return;
    }
    
    proveedoresData.forEach((proveedor, index) => {
        const avatar = generateProveedorAvatar(proveedor.nombre, index);
        
        const statusBadge = proveedor.activo ? 
            '<span class="proveedor-badge activo"><i class="fas fa-check-circle"></i> Activo</span>' : 
            '<span class="proveedor-badge inactivo"><i class="fas fa-times-circle"></i> Inactivo</span>';
            
        const tipoBadge = proveedor.tipo_proveedor ? 
            `<span class="proveedor-badge tipo"><i class="fas fa-tag"></i> ${proveedor.tipo_proveedor}</span>` : 
            '<span class="proveedor-badge tipo"><i class="fas fa-question-circle"></i> Sin tipo</span>';
        
        const row = `
            <tr>
                <td>
                    <div class="proveedor-info">
                        ${avatar}
                        <div class="proveedor-details">
                            <div class="proveedor-name">${proveedor.nombre}</div>
                            <div class="proveedor-tipo">${proveedor.tipo_proveedor || 'Sin tipo'}</div>
                        </div>
                    </div>
                </td>
                <td>${tipoBadge}</td>
                <td><span style="font-family: monospace; font-size: 12px; color: #666;">${proveedor.rfc || 'No especificado'}</span></td>
                <td><a href="mailto:${proveedor.email}" style="color: #3b82f6; text-decoration: none;">${proveedor.email}</a></td>
                <td>${statusBadge}</td>
                <td><span style="font-size: 12px; color: #666;">${proveedor.fecha_creacion ? new Date(proveedor.fecha_creacion).toLocaleDateString('es-ES') : 'N/A'}</span></td>
                <td>
                    <div class="proveedor-actions">
                        <button type="button" class="proveedor-action-btn edit btn-edit-provider" data-id="${proveedor.id}" title="Editar proveedor">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="proveedor-action-btn delete btn-delete-provider" data-id="${proveedor.id}" title="Eliminar proveedor">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        tbody.append(row);
    });
}

// Función auxiliar para obtener el badge del tipo de proveedor
function getTipoBadge(tipo) {
    switch(tipo) {
        case 'servicio':
            return '<span class="badge" style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Servicios</span>';
        case 'producto':
            return '<span class="badge" style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Productos</span>';
        case 'mixto':
            return '<span class="badge" style="background: #f59e0b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Mixto</span>';
        default:
            return '<span class="badge" style="background: #6b7280; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Sin tipo</span>';
    }
}

// Abrir modal para nuevo proveedor
function openProviderModal(providerId = null) {
    currentProviderId = providerId;
    isEditMode = providerId !== null;
    
    // Limpiar formulario
    $('#addProviderForm')[0].reset();
    $('#providerId').val('');
    
    // Limpiar personas seleccionadas
    clearSelectedPersonas();
    
    // Configurar título del modal
     const modalTitle = isEditMode ? 
         '<i class="fas fa-edit" style="color: #f59e0b; margin-right: 8px;"></i>Editar Proveedor' : 
         '<i class="fas fa-plus" style="color: #3b82f6; margin-right: 8px;"></i>Añadir Nuevo Proveedor';
     $('#addProviderModal .modal-title').html(modalTitle);
    
    if (isEditMode && providerId) {
        // Modo edición
        $('#saveProviderBtn').text('Actualizar Proveedor');
        
        // Cargar datos del proveedor para edición
        const proveedor = proveedoresData.find(p => p.id === providerId);
        if (proveedor) {
            $('#providerId').val(proveedor.id);
            $('#providerName').val(proveedor.nombre);
            $('#providerType').val(proveedor.tipo_proveedor);
            $('#providerRfc').val(proveedor.rfc);
            $('#providerEmail').val(proveedor.email);
            $('#providerPhone').val(proveedor.telefono);
            $('#providerAddress').val(proveedor.direccion);
            $('#providerStatus').val(proveedor.activo.toString());
            
            // Cargar personas de contacto si existen
            if (proveedor.contacto_principal) {
                try {
                    const personaIds = JSON.parse(proveedor.contacto_principal);
                    if (Array.isArray(personaIds)) {
                        loadPersonasForEdit(personaIds);
                    }
                } catch (e) {
                    // Si no es JSON válido, mantener el valor como texto simple
                    console.log('Contacto principal no es JSON válido:', proveedor.contacto_principal);
                }
            }
        }
    } else {
        // Modo creación
        $('#saveProviderBtn').text('Guardar Proveedor');
        $('#providerStatus').val('true');
    }
    
    // Mostrar modal usando Bootstrap 5
    const modal = new bootstrap.Modal(document.getElementById('addProviderModal'));
    modal.show();
}

// Guardar proveedor (crear o actualizar)
function saveProvider() {
    const formData = {
        nombre: $('#providerName').val().trim(),
        tipo_proveedor: $('#providerType').val(),
        rfc: $('#providerRfc').val().trim(),
        email: $('#providerEmail').val().trim(),
        telefono: $('#providerPhone').val().trim(),
        contacto_principal: $('#providerContact').val().trim(),
        direccion: $('#providerAddress').val().trim(),
        activo: $('#providerStatus').val() === 'true'
    };
    
    // Validaciones
    if (!formData.nombre) {
        showAlert('El nombre es requerido', 'error');
        return;
    }
    
    if (!formData.tipo_proveedor) {
        showAlert('El tipo de proveedor es requerido', 'error');
        return;
    }
    
    if (!formData.email) {
        showAlert('El email es requerido', 'error');
        return;
    }
    
    const providerId = $('#providerId').val();
    const isEdit = providerId && providerId !== '';
    
    const url = isEdit ? `/api/proveedores/${providerId}` : '/api/proveedores';
    const method = isEdit ? 'PUT' : 'POST';
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                $('#addProviderModal').modal('hide');
                showAlert(response.message, 'success');
                loadProveedores();
            } else {
                showAlert('Error: ' + response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            showAlert('Error de conexión al guardar proveedor', 'error');
        }
    });
}

// Ver detalles del proveedor
function viewProvider(providerId) {
    const proveedor = proveedoresData.find(p => p.id === providerId);
    if (!proveedor) {
        showAlert('Proveedor no encontrado', 'error');
        return;
    }
    
    // Crear modal de vista
    const modalContent = `
        <div class="modal fade" id="viewProviderModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Detalles del Proveedor</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Nombre:</strong> ${proveedor.nombre}</p>
                                <p><strong>Tipo:</strong> ${proveedor.tipo_proveedor || 'No especificado'}</p>
                                <p><strong>RFC:</strong> ${proveedor.rfc || 'No especificado'}</p>
                                <p><strong>Email:</strong> ${proveedor.email}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Teléfono:</strong> ${proveedor.telefono || 'No especificado'}</p>
                                <p><strong>Contacto:</strong> ${proveedor.contacto_principal || 'No especificado'}</p>
                                <p><strong>Estado:</strong> ${proveedor.activo ? 'Activo' : 'Inactivo'}</p>
                                <p><strong>Fecha de creación:</strong> ${proveedor.fecha_creacion ? new Date(proveedor.fecha_creacion).toLocaleDateString() : 'No disponible'}</p>
                            </div>
                        </div>
                        ${proveedor.direccion ? `<p><strong>Dirección:</strong> ${proveedor.direccion}</p>` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="editProvider(${proveedor.id}); $('#viewProviderModal').modal('hide');">Editar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal anterior si existe
    $('#viewProviderModal').remove();
    
    // Agregar y mostrar nuevo modal
    $('body').append(modalContent);
    $('#viewProviderModal').modal('show');
}

// Editar proveedor
function editProvider(providerId) {
    openProviderModal(providerId);
}

// Cambiar estado del proveedor
function toggleProviderStatus(providerId, newStatus) {
    const proveedor = proveedoresData.find(p => p.id === providerId);
    if (!proveedor) {
        showAlert('Proveedor no encontrado', 'error');
        return;
    }
    
    const action = newStatus ? 'activar' : 'desactivar';
    
    if (confirm(`¿Está seguro que desea ${action} este proveedor?`)) {
        $.ajax({
            url: `/api/proveedores/${providerId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ activo: newStatus }),
            success: function(response) {
                if (response.success) {
                    showAlert(`Proveedor ${action}do exitosamente`, 'success');
                    loadProveedores();
                    loadEstadisticas();
                } else {
                    showAlert('Error: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showAlert('Error de conexión al cambiar estado', 'error');
            }
        });
    }
}

// Eliminar proveedor
function deleteProvider(providerId) {
    const proveedor = proveedoresData.find(p => p.id === providerId);
    if (!proveedor) {
        showAlert('Proveedor no encontrado', 'error');
        return;
    }
    
    if (confirm(`¿Está seguro que desea eliminar el proveedor "${proveedor.nombre}"?\n\nEsta acción marcará el proveedor como inactivo.`)) {
        $.ajax({
            url: `/api/proveedores/${providerId}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    loadProveedores();
                    loadEstadisticas();
                } else {
                    showAlert('Error: ' + response.message, 'error');
                }
            },
            error: function(xhr, status, error) {
                showAlert('Error de conexión al eliminar proveedor', 'error');
            }
        });
    }
}



// Función para mostrar/ocultar barra de búsqueda
function toggleSearchBar() {
    const searchContainer = $('#searchContainer');
    const searchInput = $('#searchInput');
    
    if (searchContainer.is(':visible')) {
        searchContainer.slideUp(200);
        searchInput.val('');
        // Mostrar todos los proveedores al cerrar búsqueda
        filterProviders('');
    } else {
        searchContainer.slideDown(200, function() {
            searchInput.focus();
        });
    }
}

// Función para filtrar proveedores
function filterProviders(searchTerm) {
    const rows = $('#providersTableBody tr');
    
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

// Función para buscar personas responsables
function searchPersonas(searchTerm) {
    $.ajax({
        url: '/personas/api/search',
        method: 'GET',
        data: { q: searchTerm },
        success: function(response) {
            displayPersonaResults(response.personas);
        },
        error: function(xhr, status, error) {
            console.error('Error al buscar personas:', error);
            $('#personaSearchResults').hide().removeClass('show');
        }
    });
}

// Función para mostrar resultados de búsqueda de personas
function displayPersonaResults(personas) {
    const resultsContainer = $('#personaSearchResults');
    resultsContainer.empty();
    
    if (personas.length === 0) {
        resultsContainer.append('<div class="dropdown-item-text">No se encontraron personas</div>');
    } else {
        personas.forEach(persona => {
            // Verificar si ya está seleccionada
            const isSelected = selectedPersonas.some(p => p.id === persona.id);
            if (!isSelected) {
                const item = $(`
                    <div class="dropdown-item" data-persona-id="${persona.id}">
                        <div class="persona-info">
                            <div class="persona-name">${persona.nombre}</div>
                            <div class="persona-details">${persona.cargo || 'Sin cargo'} - ${persona.email || 'Sin email'}</div>
                        </div>
                    </div>
                `);
                
                item.on('click', function() {
                    selectPersona(persona);
                });
                
                resultsContainer.append(item);
            }
        });
    }
    
    resultsContainer.addClass('show').show();
}

// Función para seleccionar una persona
function selectPersona(persona) {
    // Agregar a la lista de seleccionados
    selectedPersonas.push(persona);
    
    // Limpiar el input de búsqueda
    $('#personaSearch').val('');
    $('#personaSearchResults').hide().removeClass('show');
    
    // Actualizar la visualización
    updateSelectedPersonasDisplay();
    updateProviderContactField();
}

// Función para actualizar la visualización de personas seleccionadas
function updateSelectedPersonasDisplay() {
    const container = $('#selectedPersonas');
    container.empty();
    
    selectedPersonas.forEach((persona, index) => {
        const tag = $(`
            <span class="persona-tag">
                ${persona.nombre}
                <span class="remove-persona" data-index="${index}">&times;</span>
            </span>
        `);
        
        tag.find('.remove-persona').on('click', function() {
            removePersona(index);
        });
        
        container.append(tag);
    });
}

// Función para remover una persona seleccionada
function removePersona(index) {
    selectedPersonas.splice(index, 1);
    updateSelectedPersonasDisplay();
    updateProviderContactField();
}

// Función para actualizar el campo oculto con las personas seleccionadas
function updateProviderContactField() {
    const personasIds = selectedPersonas.map(p => p.id);
    $('#providerContact').val(JSON.stringify(personasIds));
}

// Función para mostrar los resultados de la búsqueda
function showPersonaResults(personas) {
    const resultsContainer = $('#personaSearchResults');
    resultsContainer.empty();
    
    if (personas.length === 0) {
        resultsContainer.append('<div class="dropdown-item text-muted">No se encontraron personas</div>');
    } else {
        personas.forEach(persona => {
            // Verificar si ya está seleccionada
            const isSelected = selectedPersonas.some(p => p.id === persona.id);
            if (!isSelected) {
                const item = $(`
                    <div class="dropdown-item" data-persona-id="${persona.id}">
                        <div class="persona-info">
                            <div class="persona-name">${persona.nombre}</div>
                            <div class="persona-details">${persona.cargo || 'Sin cargo'} - ${persona.email || 'Sin email'}</div>
                        </div>
                    </div>
                `);
                
                item.on('click', function() {
                    selectPersona(persona);
                });
                
                resultsContainer.append(item);
            }
        });
    }
    
    resultsContainer.show();
}

// Función para ocultar los resultados de la búsqueda
function hidePersonaResults() {
    $('#personaSearchResults').hide().empty();
}

// Función para cargar personas en modo edición
function loadPersonasForEdit(personaIds) {
    if (!personaIds || personaIds.length === 0) return;
    
    $.ajax({
        url: '/personas/api/get_by_ids',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ ids: personaIds }),
        success: function(response) {
            if (response.success && response.personas) {
                selectedPersonas = response.personas;
                updateSelectedPersonasDisplay();
                updateProviderContactField();
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar personas para edición:', error);
        }
    });
}



function clearSelectedPersonas() {
    selectedPersonas = [];
    updateSelectedPersonasDisplay();
    updateProviderContactField();
}

// Función para mostrar alertas
function showAlert(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remover alertas anteriores
    $('.alert').remove();
    
    // Agregar nueva alerta al inicio del contenido
    $('.content-wrapper').prepend(alertHtml);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        $('.alert').fadeOut();
    }, 5000);
}