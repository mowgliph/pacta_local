// Gestión de Personas Responsables
let personas = [];
let filteredPersonas = [];
let currentSort = { field: null, direction: 'asc' };
let searchActive = false;

// Función para generar avatar de persona con color basado en el nombre
function generatePersonaAvatar(nombre) {
    if (!nombre) return '<div class="persona-avatar color-blue">?</div>';
    
    const words = nombre.trim().split(' ');
    let initials = '';
    
    if (words.length >= 2) {
        initials = words[0][0] + words[1][0];
    } else {
        initials = words[0][0] + (words[0][1] || '');
    }
    
    // Generar color basado en el hash del nombre
    const colors = ['blue', 'green', 'purple', 'pink', 'orange', 'red', 'indigo', 'teal'];
    let hash = 0;
    for (let i = 0; i < nombre.length; i++) {
        hash = nombre.charCodeAt(i) + ((hash << 5) - hash);
    }
    const colorIndex = Math.abs(hash) % colors.length;
    const colorClass = colors[colorIndex];
    
    return `<div class="persona-avatar color-${colorClass}" title="${nombre}">${initials.toUpperCase()}</div>`;
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    loadPersonas();
    loadPersonasMetrics();
    initializeEventListeners();
});

// Configurar event listeners
function initializeEventListeners() {
    // Botón añadir persona
    document.getElementById('btnAddPersona').addEventListener('click', function() {
        openPersonaModal();
    });
    
    // Botón buscar
    document.getElementById('btnSearchPersona').addEventListener('click', function() {
        toggleSearch();
    });
    
    // Input de búsqueda
    document.getElementById('searchInput').addEventListener('input', function() {
        filterPersonas(this.value);
    });
    
    // Botón guardar persona
    document.getElementById('savePersonaBtn').addEventListener('click', function() {
        savePersona();
    });
    
    // Configurar ordenamiento de tabla
    setupTableSorting();
}

// Cargar personas desde el servidor
function loadPersonas() {
    fetch('/api/personas')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                personas = data.personas;
                filteredPersonas = [...personas];
                renderPersonasTable();
            } else {
                showError('Error al cargar personas: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error al cargar personas');
        });
}

// Función para cargar métricas dinámicamente
function loadPersonasMetrics() {
    $.ajax({
        url: '/api/personas/estadisticas',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                updateMetricCards(response.estadisticas);
            } else {
                console.error('Error al cargar estadísticas:', response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar estadísticas de personas:', error);
        }
    });
}

// Función para actualizar las tarjetas de métricas
function updateMetricCards(estadisticas) {
    // Actualizar total de personas
    const totalElement = document.querySelector('[data-metric="total-personas"] .metric-value');
    if (totalElement) {
        totalElement.textContent = estadisticas.total_personas;
    }
    
    // Actualizar personas activas
    const activasElement = document.querySelector('[data-metric="personas-activas"] .metric-value');
    if (activasElement) {
        activasElement.textContent = estadisticas.personas_activas;
    }
    
    // Actualizar porcentaje de activas
    const porcentajeActivasElement = document.querySelector('[data-metric="personas-activas"] .metric-change');
    if (porcentajeActivasElement) {
        porcentajeActivasElement.textContent = `${estadisticas.porcentaje_activas}% del total`;
    }
    
    // Actualizar personas principales
    const principalesElement = document.querySelector('[data-metric="personas-principales"] .metric-value');
    if (principalesElement) {
        principalesElement.textContent = estadisticas.personas_principales;
    }
    
    // Actualizar porcentaje de principales
    const porcentajePrincipalesElement = document.querySelector('[data-metric="personas-principales"] .metric-change');
    if (porcentajePrincipalesElement) {
        porcentajePrincipalesElement.textContent = `${estadisticas.porcentaje_principales}% del total`;
    }
    
    // Actualizar clientes con personas
    const clientesElement = document.querySelector('[data-metric="clientes-con-personas"] .metric-value');
    if (clientesElement) {
        clientesElement.textContent = estadisticas.clientes_con_personas;
    }
}

// Renderizar tabla de personas
function renderPersonasTable() {
    const tbody = document.getElementById('personasTableBody');
    tbody.innerHTML = '';
    
    if (filteredPersonas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <i class="fas fa-users fa-2x text-muted mb-2"></i>
                    <p class="text-muted mb-0">No se encontraron personas responsables</p>
                </td>
            </tr>
        `;
        return;
    }
    
    filteredPersonas.forEach(persona => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        ${generatePersonaAvatar(persona.nombre)}
                    </div>
                    <div>
                        <div class="fw-medium">${persona.nombre}</div>
                        ${persona.cargo ? `<small class="text-muted">${persona.cargo}</small>` : ''}
                    </div>
                </div>
            </td>
            <td>
                <span class="persona-badge ${persona.cliente_nombre ? 'secundaria' : 'inactivo'}">
                    <i class="fas ${persona.cliente_nombre ? 'fa-building' : 'fa-exclamation-triangle'}"></i>
                    ${persona.cliente_nombre || 'Sin cliente'}
                </span>
            </td>
            <td>${persona.cargo || '-'}</td>
            <td>
                ${persona.email ? `<a href="mailto:${persona.email}" class="text-decoration-none">${persona.email}</a>` : '-'}
            </td>
            <td>
                ${persona.telefono ? `<a href="tel:${persona.telefono}" class="text-decoration-none">${persona.telefono}</a>` : '-'}
            </td>
            <td>
                <span class="persona-badge ${persona.es_principal ? 'principal' : 'secundaria'}">
                    <i class="fas ${persona.es_principal ? 'fa-star' : 'fa-user'}"></i>
                    ${persona.es_principal ? 'Principal' : 'Secundaria'}
                </span>
            </td>
            <td>
                <span class="persona-badge ${persona.activo ? 'activo' : 'inactivo'}">
                    <i class="fas ${persona.activo ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                    ${persona.activo ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td>
                <div class="persona-actions">
                    <button type="button" class="persona-action-btn view" onclick="viewPersona(${persona.id})" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="persona-action-btn edit" onclick="editPersona(${persona.id})" title="Editar persona">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="persona-action-btn delete" onclick="deletePersona(${persona.id})" title="Eliminar persona">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Abrir modal de persona (crear o editar)
function openPersonaModal(personaId = null) {
    const modal = new bootstrap.Modal(document.getElementById('addPersonaModal'));
    const modalTitle = document.querySelector('#addPersonaModal .modal-title');
    const form = document.getElementById('addPersonaForm');
    const documentoInput = document.getElementById('personaDocumento');
    const currentDocInfo = document.getElementById('currentDocumentInfo');
    
    // Limpiar formulario
    form.reset();
    document.getElementById('personaId').value = '';
    currentDocInfo.style.display = 'none';
    currentDocInfo.innerHTML = '';
    
    if (personaId) {
        // Modo edición
        modalTitle.innerHTML = '<i class="fas fa-edit" style="color: #f59e0b; margin-right: 8px;"></i>Editar Persona Responsable';
        documentoInput.removeAttribute('required'); // No requerido en edición
        loadPersonaForEdit(personaId);
    } else {
        // Modo creación
        modalTitle.innerHTML = '<i class="fas fa-plus" style="color: #3b82f6; margin-right: 8px;"></i>Añadir Nueva Persona Responsable';
        documentoInput.setAttribute('required', 'required'); // Requerido en creación
    }
    
    modal.show();
}

// Cargar datos de persona para edición
function loadPersonaForEdit(personaId) {
    const persona = personas.find(p => p.id === personaId);
    if (persona) {
        document.getElementById('personaId').value = persona.id;
        document.getElementById('personaNombre').value = persona.nombre;
        document.getElementById('personaCargo').value = persona.cargo || '';
        document.getElementById('personaEmail').value = persona.email || '';
        document.getElementById('personaTelefono').value = persona.telefono || '';
        document.getElementById('personaActivo').value = persona.activo.toString();
        document.getElementById('personaEsPrincipal').checked = persona.es_principal;
        document.getElementById('personaObservaciones').value = persona.observaciones || '';
        
        // Mostrar información del documento actual si existe
        const currentDocInfo = document.getElementById('currentDocumentInfo');
        const documentoInput = document.getElementById('personaDocumento');
        
        if (persona.documento_path) {
            // Extraer nombre del archivo de la ruta
            const fileName = persona.documento_path.split('/').pop().split('\\').pop();
            currentDocInfo.innerHTML = `
                <div class="alert alert-info d-flex align-items-center" style="margin-bottom: 10px;">
                    <i class="fas fa-file-alt me-2"></i>
                    <div class="flex-grow-1">
                        <strong>Documento actual:</strong> ${fileName}
                        <br><small class="text-muted">Selecciona un nuevo archivo para reemplazarlo</small>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-primary ms-2" onclick="previewCurrentDocument('${persona.documento_path}')">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                </div>
            `;
            currentDocInfo.style.display = 'block';
        } else {
            currentDocInfo.innerHTML = '';
            currentDocInfo.style.display = 'none';
        }
        
        // Limpiar el input de archivo
        documentoInput.value = '';
    }
}

// Guardar persona (crear o actualizar)
function savePersona() {
    const form = document.getElementById('addPersonaForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const personaId = document.getElementById('personaId').value;
    const formData = new FormData();
    formData.append('nombre', document.getElementById('personaNombre').value);
    formData.append('cargo', document.getElementById('personaCargo').value);
    formData.append('email', document.getElementById('personaEmail').value);
    formData.append('telefono', document.getElementById('personaTelefono').value);
    formData.append('activo', document.getElementById('personaActivo').value === 'true');
    formData.append('es_principal', document.getElementById('personaEsPrincipal').checked);
    formData.append('observaciones', document.getElementById('personaObservaciones').value);
    
    // Agregar archivo si existe
    const documentoFile = document.getElementById('personaDocumento').files[0];
    if (documentoFile) {
        formData.append('documento', documentoFile);
    }
    
    const url = personaId ? `/personas/editar/${personaId}` : '/personas/crear';
    const method = 'POST';
    
    fetch(url, {
        method: method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(data.message || (personaId ? 'Persona actualizada correctamente' : 'Persona creada correctamente'));
            bootstrap.Modal.getInstance(document.getElementById('addPersonaModal')).hide();
            loadPersonas(); // Recargar la lista
            loadPersonasMetrics(); // Actualizar métricas
        } else {
            showError(data.message || 'Error al guardar la persona');
        }
    })
    .catch(error => {
        console.error('Error al guardar persona:', error);
        showError('Error de conexión al guardar la persona');
    });
}

// Editar persona
function editPersona(personaId) {
    openPersonaModal(personaId);
}

// Eliminar persona
function deletePersona(personaId) {
    const persona = personas.find(p => p.id === personaId);
    if (!persona) {
        showError('Persona no encontrada');
        return;
    }
    
    // Usar modal de confirmación personalizado
    const message = `
        <strong>Esta acción eliminará permanentemente:</strong>
        <br><br>
        • Los datos de <strong>${persona.nombre}</strong><br>
        • Todos sus documentos asociados<br>
        • Su historial de actividades<br>
        <br>
        <span class="text-danger"><strong>Esta acción no se puede deshacer.</strong></span>
    `;
    
    showDeleteConfirmModal(
        persona.nombre,
        () => {
            // Proceder con la eliminación
            fetch(`/personas/eliminar/${personaId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showSuccess(data.message);
                    loadPersonas(); // Recargar la lista
                    loadPersonasMetrics(); // Actualizar métricas
                } else {
                    showError(data.message || 'Error al eliminar la persona');
                }
            })
            .catch(error => {
                console.error('Error al eliminar persona:', error);
                showError('Error de conexión al eliminar la persona');
            });
        }
    );
}

// Toggle búsqueda
function toggleSearch() {
    const searchContainer = document.getElementById('searchContainer');
    const searchInput = document.getElementById('searchInput');
    
    searchActive = !searchActive;
    
    if (searchActive) {
        searchContainer.style.display = 'block';
        searchInput.focus();
    } else {
        searchContainer.style.display = 'none';
        searchInput.value = '';
        filteredPersonas = [...personas];
        renderPersonasTable();
    }
}

// Filtrar personas
function filterPersonas(searchTerm) {
    if (!searchTerm.trim()) {
        filteredPersonas = [...personas];
    } else {
        const term = searchTerm.toLowerCase();
        filteredPersonas = personas.filter(persona => 
            persona.nombre.toLowerCase().includes(term) ||
            (persona.cliente_nombre && persona.cliente_nombre.toLowerCase().includes(term)) ||
            (persona.cargo && persona.cargo.toLowerCase().includes(term)) ||
            (persona.email && persona.email.toLowerCase().includes(term)) ||
            (persona.telefono && persona.telefono.includes(term))
        );
    }
    renderPersonasTable();
}

// Configurar ordenamiento de tabla
function setupTableSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const field = this.textContent.trim().toLowerCase();
            sortPersonas(field);
        });
    });
}

// Ordenar personas
function sortPersonas(field) {
    // Mapear nombres de columnas a campos de datos
    const fieldMap = {
        'nombre': 'nombre',
        'cliente': 'cliente_nombre',
        'cargo': 'cargo',
        'email': 'email',
        'teléfono': 'telefono',
        'principal': 'es_principal',
        'estado': 'activo'
    };
    
    const dataField = fieldMap[field] || field;
    
    if (currentSort.field === dataField) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = dataField;
        currentSort.direction = 'asc';
    }
    
    filteredPersonas.sort((a, b) => {
        let aVal = a[dataField] || '';
        let bVal = b[dataField] || '';
        
        // Convertir a string para comparación
        aVal = aVal.toString().toLowerCase();
        bVal = bVal.toString().toLowerCase();
        
        if (currentSort.direction === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
    
    renderPersonasTable();
    updateSortIcons();
}

// Actualizar iconos de ordenamiento
function updateSortIcons() {
    const sortIcons = document.querySelectorAll('.sort-icon');
    sortIcons.forEach(icon => {
        icon.innerHTML = '';
    });
    
    if (currentSort.field) {
        const activeHeader = document.querySelector(`.sortable:nth-child(${getSortColumnIndex()})`);
        if (activeHeader) {
            const icon = activeHeader.querySelector('.sort-icon');
            icon.innerHTML = currentSort.direction === 'asc' ? '↑' : '↓';
        }
    }
}

// Obtener índice de columna para ordenamiento
function getSortColumnIndex() {
    const fieldMap = {
        'nombre': 1,
        'cliente_nombre': 2,
        'cargo': 3,
        'email': 4,
        'telefono': 5,
        'es_principal': 6,
        'activo': 7
    };
    return fieldMap[currentSort.field] || 1;
}

// Ver detalles de persona
function viewPersona(personaId) {
    const persona = personas.find(p => p.id === personaId);
    if (!persona) {
        showError('Persona no encontrada');
        return;
    }
    
    // Crear modal de vista previa
    const modalHtml = `
        <div class="modal fade" id="viewPersonaModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-eye" style="color: #10b981; margin-right: 8px;"></i>
                            Detalles de Persona Responsable
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <!-- Información del Usuario -->
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-header">
                                        <h6 class="mb-0"><i class="fas fa-user me-2"></i>Información Personal</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="me-3">
                                                ${generatePersonaAvatar(persona.nombre)}
                                            </div>
                                            <div>
                                                <h5 class="mb-1">${persona.nombre}</h5>
                                                <span class="badge ${persona.es_principal ? 'bg-warning' : 'bg-secondary'}">
                                                    <i class="fas ${persona.es_principal ? 'fa-star' : 'fa-user'}"></i>
                                                    ${persona.es_principal ? 'Principal' : 'Secundaria'}
                                                </span>
                                            </div>
                                        </div>
                                        
                                        <div class="mb-2">
                                            <strong>Cargo:</strong> ${persona.cargo || 'No especificado'}
                                        </div>
                                        <div class="mb-2">
                                            <strong>Email:</strong> 
                                            ${persona.email ? `<a href="mailto:${persona.email}">${persona.email}</a>` : 'No especificado'}
                                        </div>
                                        <div class="mb-2">
                                            <strong>Teléfono:</strong> 
                                            ${persona.telefono ? `<a href="tel:${persona.telefono}">${persona.telefono}</a>` : 'No especificado'}
                                        </div>
                                        <div class="mb-2">
                                            <strong>Cliente:</strong> ${persona.cliente_nombre || 'Sin cliente asignado'}
                                        </div>
                                        <div class="mb-2">
                                            <strong>Estado:</strong> 
                                            <span class="badge ${persona.activo ? 'bg-success' : 'bg-danger'}">
                                                <i class="fas ${persona.activo ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                                                ${persona.activo ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </div>
                                        ${persona.observaciones ? `
                                            <div class="mb-2">
                                                <strong>Observaciones:</strong><br>
                                                <small class="text-muted">${persona.observaciones}</small>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Vista Previa del Documento -->
                            <div class="col-md-6">
                                <div class="card h-100">
                                    <div class="card-header">
                                        <h6 class="mb-0"><i class="fas fa-file-alt me-2"></i>Documento Oficial</h6>
                                    </div>
                                    <div class="card-body">
                                        <div id="documentPreview">
                                            ${persona.documento_path ? generateDocumentPreview(persona.documento_path) : `
                                                <div class="text-center text-muted" style="padding: 40px;">
                                                    <i class="fas fa-file-slash fa-3x mb-3"></i>
                                                    <p>No hay documento disponible</p>
                                                    <small>Esta persona no tiene un documento oficial subido</small>
                                                </div>
                                            `}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-primary" onclick="editPersona(${persona.id}); bootstrap.Modal.getInstance(document.getElementById('viewPersonaModal')).hide();">
                            <i class="fas fa-edit me-1"></i>Editar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si existe
    const existingModal = document.getElementById('viewPersonaModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('viewPersonaModal'));
    modal.show();
    
    // Limpiar modal cuando se cierre
    document.getElementById('viewPersonaModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Función para generar vista previa del documento
function generateDocumentPreview(documentPath) {
    if (!documentPath) {
        return `
            <div class="text-center text-muted" style="padding: 40px;">
                <i class="fas fa-file-slash fa-3x mb-3"></i>
                <p>No hay documento disponible</p>
                <small>Esta persona no tiene un documento oficial subido</small>
            </div>
        `;
    }
    
    // Obtener extensión del archivo
    const extension = documentPath.split('.').pop().toLowerCase();
    // Construir la ruta correcta del archivo
    const fullPath = documentPath.startsWith('/') ? documentPath : `/${documentPath}`;
    
    // Tipos de archivo de imagen
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'];
    
    // Tipos de archivo de documento
    const documentExtensions = {
        'pdf': { icon: 'fa-file-pdf', color: 'text-danger', name: 'PDF' },
        'doc': { icon: 'fa-file-word', color: 'text-primary', name: 'Word' },
        'docx': { icon: 'fa-file-word', color: 'text-primary', name: 'Word' },
        'xls': { icon: 'fa-file-excel', color: 'text-success', name: 'Excel' },
        'xlsx': { icon: 'fa-file-excel', color: 'text-success', name: 'Excel' },
        'ppt': { icon: 'fa-file-powerpoint', color: 'text-warning', name: 'PowerPoint' },
        'pptx': { icon: 'fa-file-powerpoint', color: 'text-warning', name: 'PowerPoint' },
        'txt': { icon: 'fa-file-alt', color: 'text-secondary', name: 'Texto' },
        'zip': { icon: 'fa-file-archive', color: 'text-info', name: 'Archivo' },
        'rar': { icon: 'fa-file-archive', color: 'text-info', name: 'Archivo' }
    };
    
    if (imageExtensions.includes(extension)) {
        // Vista previa para imágenes
        return `
            <div class="text-center">
                <div class="document-preview-container" style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 15px; background: #f8fafc;">
                    <div class="mb-3">
                        <img src="${fullPath}" 
                             alt="Vista previa del documento" 
                             style="max-width: 100%; max-height: 300px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div style="display: none; padding: 40px;" class="text-muted">
                            <i class="fas fa-image fa-3x mb-3"></i>
                            <p>Error al cargar la imagen</p>
                        </div>
                    </div>
                    <div class="d-flex justify-content-center gap-2">
                        <a href="${fullPath}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-external-link-alt me-1"></i>
                            Ver Original
                        </a>
                        <a href="${fullPath}" download class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-download me-1"></i>
                            Descargar
                        </a>
                    </div>
                </div>
            </div>
        `;
    } else if (extension === 'pdf') {
        // Vista previa para PDFs usando iframe
        return `
            <div class="text-center">
                <div class="document-preview-container" style="border: 2px solid #e2e8f0; border-radius: 8px; overflow: hidden; background: #f8fafc;">
                    <div style="height: 350px; position: relative;">
                        <iframe src="${fullPath}" 
                                style="width: 100%; height: 100%; border: none;" 
                                onload="this.style.display='block'; this.nextElementSibling.style.display='none';" 
                                onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        </iframe>
                        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; padding: 20px;" class="text-center">
                            <i class="fas fa-file-pdf fa-4x text-danger mb-3"></i>
                            <p class="mb-2"><strong>Documento PDF</strong></p>
                            <p class="text-muted mb-3">Vista previa no disponible en este navegador</p>
                        </div>
                    </div>
                    <div class="p-3 border-top bg-white">
                        <div class="d-flex justify-content-center gap-2">
                            <a href="${fullPath}" target="_blank" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-external-link-alt me-1"></i>
                                Abrir PDF
                            </a>
                            <a href="${fullPath}" download class="btn btn-outline-secondary btn-sm">
                                <i class="fas fa-download me-1"></i>
                                Descargar
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Vista previa para otros tipos de documento
        const docInfo = documentExtensions[extension] || { icon: 'fa-file', color: 'text-secondary', name: 'Documento' };
        
        return `
            <div class="text-center">
                <div class="document-preview-container" style="border: 2px dashed #e2e8f0; border-radius: 8px; padding: 30px; min-height: 250px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #f8fafc;">
                    <i class="fas ${docInfo.icon} fa-4x ${docInfo.color} mb-3"></i>
                    <p class="mb-2"><strong>Archivo ${docInfo.name}</strong></p>
                    <p class="text-muted mb-3">Documento disponible para descarga</p>
                    <small class="text-muted mb-3">Tipo: ${extension.toUpperCase()}</small>
                    <div class="d-flex gap-2">
                        <a href="${fullPath}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-external-link-alt me-1"></i>
                            Abrir
                        </a>
                        <a href="${fullPath}" download class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-download me-1"></i>
                            Descargar
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
}

// Función para previsualizar el documento actual en modo edición
function previewCurrentDocument(documentPath) {
    const modal = new bootstrap.Modal(document.getElementById('previewDocumentModal') || createPreviewModal());
    const modalBody = document.querySelector('#previewDocumentModal .modal-body');
    
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="document-preview">
                ${generateDocumentPreview(documentPath)}
            </div>
        `;
        modal.show();
    }
}

// Crear modal de vista previa si no existe
function createPreviewModal() {
    const modalHtml = `
        <div class="modal fade" id="previewDocumentModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-eye" style="color: #10b981; margin-right: 8px;"></i>
                            Vista Previa del Documento
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Contenido dinámico -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Limpiar modal cuando se cierre
    document.getElementById('previewDocumentModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
    
    return document.getElementById('previewDocumentModal');
}

