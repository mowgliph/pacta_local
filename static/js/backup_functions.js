// Funciones para la gestión de backups

// Funciones de utilidad para mostrar mensajes usando el sistema unificado de toasts
function showSuccess(message) {
    if (window.toastManager) {
        window.toastManager.showSuccess(message);
    } else {
        alert(message);
    }
}

function showError(message) {
    if (window.toastManager) {
        window.toastManager.showError(message);
    } else {
        alert(message);
    }
}

// Función para mostrar opciones de restauración
function showRestoreOptions() {
    // Obtener lista de backups disponibles
    fetch('/api/backup/list')
        .then(response => response.json())
        .then(data => {
            if (data.success && (data.backups.automatic.length > 0 || data.backups.manual.length > 0)) {
                // Combinar todos los backups y ordenar por fecha
                const allBackups = [];
                
                // Agregar backups automáticos
                if (data.backups.automatic) {
                    data.backups.automatic.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'automatic',
                            typeText: 'Automático'
                        });
                    });
                }
                
                // Agregar backups manuales
                if (data.backups.manual) {
                    data.backups.manual.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'manual',
                            typeText: 'Manual'
                        });
                    });
                }
                
                // Agregar backups importados
                if (data.backups.imported) {
                    data.backups.imported.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'imported',
                            typeText: 'Importado'
                        });
                    });
                }
                
                // Ordenar por fecha de creación (más reciente primero)
                allBackups.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                
                // Crear modal con opciones de restauración
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-undo me-2"></i>
                                    Seleccionar Backup para Restaurar
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="alert alert-warning">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    <strong>Advertencia:</strong> La restauración sobrescribirá todos los datos actuales del sistema.
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Backup</th>
                                                <th>Tipo</th>
                                                <th>Tamaño</th>
                                                <th>Acción</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${allBackups.map(backup => {
                                                // Formatear fecha
                                                const formattedDate = backup.created_at ? 
                                                    new Date(backup.created_at).toLocaleString('es-ES', {
                                                        year: 'numeric',
                                                        month: '2-digit',
                                                        day: '2-digit',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    }) : 'Fecha desconocida';
                                                
                                                // Formatear tamaño
                                                const formattedSize = backup.size_mb ? `${backup.size_mb} MB` : 'Tamaño desconocido';
                                                
                                                const typeClass = backup.type === 'automatic' ? 'backup-type-auto' : 'backup-type-manual';
                                                
                                                return `
                                                    <tr>
                                                        <td>
                                                            <div class="backup-name">${backup.name}</div>
                                                            <small class="text-muted">${formattedDate}</small>
                                                        </td>
                                                        <td>
                                                            <span class="badge ${typeClass}">${backup.typeText}</span>
                                                        </td>
                                                        <td>${formattedSize}</td>
                                                        <td>
                                                            <button class="btn btn-success btn-sm" 
                                                                    onclick="prepareRestore('${backup.type}', '${backup.name}')">
                                                                <i class="fas fa-undo me-1"></i>
                                                                Restaurar
                                                            </button>
                                                        </td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-primary" onclick="showImportBackupModal()">
                                    <i class="fas fa-upload me-2"></i>
                                    Importar Backup
                                </button>
                                <button type="button" class="btn btn-danger" onclick="showDeleteImportsModal()">
                                    <i class="fas fa-trash me-2"></i>
                                    Eliminar Importaciones
                                </button>
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Agregar modal al DOM y mostrarlo
                document.body.appendChild(modal);
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
                
                // Limpiar modal cuando se cierre
                modal.addEventListener('hidden.bs.modal', () => {
                    document.body.removeChild(modal);
                });
            } else {
                showError('No hay backups disponibles para restaurar');
            }
        })
        .catch(error => {
            showError('Error al cargar backups: ' + error.message);
        });
}

// Función para mostrar opciones de descarga
function showDownloadOptions() {
    // Obtener lista de backups disponibles
    fetch('/api/backup/list')
        .then(response => response.json())
        .then(data => {
            if (data.success && (data.backups.automatic.length > 0 || data.backups.manual.length > 0)) {
                // Combinar todos los backups y ordenar por fecha
                const allBackups = [];
                
                // Agregar backups automáticos
                if (data.backups.automatic) {
                    data.backups.automatic.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'automatic',
                            typeText: 'Automático'
                        });
                    });
                }
                
                // Agregar backups manuales
                if (data.backups.manual) {
                    data.backups.manual.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'manual',
                            typeText: 'Manual'
                        });
                    });
                }
                
                // Agregar backups importados
                if (data.backups.imported) {
                    data.backups.imported.forEach(backup => {
                        allBackups.push({
                            ...backup,
                            type: 'imported',
                            typeText: 'Importado'
                        });
                    });
                }

                // Ordenar por fecha de creación (más reciente primero)
                allBackups.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                
                // Crear modal con opciones de descarga
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-download me-2"></i>
                                    Seleccionar Backup para Descargar
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    Selecciona el backup que deseas descargar. El archivo se guardará en tu carpeta de descargas.
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th>Backup</th>
                                                <th>Tipo</th>
                                                <th>Tamaño</th>
                                                <th>Acción</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${allBackups.map(backup => {
                                                // Formatear fecha
                                                const formattedDate = backup.created_at ? 
                                                    new Date(backup.created_at).toLocaleString('es-ES', {
                                                        year: 'numeric',
                                                        month: '2-digit',
                                                        day: '2-digit',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    }) : 'Fecha desconocida';
                                                
                                                // Formatear tamaño
                                                const formattedSize = backup.size_mb ? `${backup.size_mb} MB` : 'Tamaño desconocido';
                                                
                                                const typeClass = backup.type === 'automatic' ? 'backup-type-auto' : 'backup-type-manual';
                                                
                                                return `
                                                    <tr>
                                                        <td>
                                                            <div class="backup-name">${backup.name}</div>
                                                            <small class="text-muted">${formattedDate}</small>
                                                        </td>
                                                        <td>
                                                            <span class="badge ${typeClass}">${backup.typeText}</span>
                                                        </td>
                                                        <td>${formattedSize}</td>
                                                        <td>
                                                            <button class="btn btn-primary btn-sm" 
                                                                    onclick="downloadBackup('${backup.type}', '${backup.name}')">
                                                                <i class="fas fa-download me-1"></i>
                                                                Descargar
                                                            </button>
                                                        </td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Agregar modal al DOM y mostrarlo
                document.body.appendChild(modal);
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
                
                // Limpiar modal cuando se cierre
                modal.addEventListener('hidden.bs.modal', () => {
                    document.body.removeChild(modal);
                });
            } else {
                showError('No hay backups disponibles para descargar');
            }
        })
        .catch(error => {
            showError('Error al cargar backups: ' + error.message);
        });
}

// Función para limpiar backups antiguos
async function cleanupOldBackups() {
    if (!confirm('¿Estás seguro de que deseas limpiar los backups antiguos? Esta acción eliminará backups automáticos con más de 7 días.')) {
        return;
    }
    
    const btn = document.getElementById('cleanupToolBtn');
    const originalText = btn.innerHTML;
    
    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Limpiando...';
        
        const response = await fetch('/api/backup/cleanup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Limpieza completada. ${data.deleted_count || 0} backups eliminados.`);
            loadBackupData();
        } else {
            throw new Error(data.message || 'Error al limpiar backups');
        }
    } catch (error) {
        showError('Error al limpiar backups: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Función para crear backup (ya existente, mantenida para compatibilidad)
// Función para mostrar el modal de crear backup
function showCreateBackupModal() {
    // Generar nombre por defecto
    const now = new Date();
    const defaultName = `Backup_Manual_${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}-${String(now.getMinutes()).padStart(2, '0')}`;
    
    document.getElementById('backupName').value = defaultName;
    document.getElementById('backupDescription').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('createBackupModal'));
    modal.show();
}

// Función para crear backup con nombre personalizado
function createBackupWithName() {
    const backupName = document.getElementById('backupName').value.trim();
    const backupDescription = document.getElementById('backupDescription').value.trim();
    
    if (!backupName) {
        showError('El nombre del backup es requerido');
        return;
    }
    
    // Validar nombre (solo letras, números, guiones y guiones bajos)
    const nameRegex = /^[a-zA-Z0-9_-]+$/;
    if (!nameRegex.test(backupName)) {
        showError('El nombre solo puede contener letras, números, guiones y guiones bajos');
        return;
    }
    
    const btn = document.getElementById('confirmCreateBtn');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
    
    const requestData = {
        name: backupName
    };
    
    if (backupDescription) {
        requestData.description = backupDescription;
    }
    
    fetch('/api/backup/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Backup creado exitosamente');
            loadBackupData();
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createBackupModal'));
            modal.hide();
        } else {
            throw new Error(data.message || 'Error al crear backup');
        }
    })
    .catch(error => {
        showError('Error al crear backup: ' + error.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Función original para compatibilidad (ahora llama al modal)
function createBackup() {
    showCreateBackupModal();
}

// Función para mostrar el modal de configuración de backups automáticos
function showAutoBackupConfigModal() {
    // Cargar configuración actual
    loadAutoBackupConfig();
    
    const modal = new bootstrap.Modal(document.getElementById('autoBackupConfigModal'));
    modal.show();
}

// Función para cargar la configuración actual de backups automáticos
function loadAutoBackupConfig() {
    fetch('/api/backup/config')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const config = data.config;
                document.getElementById('autoBackupEnabled').checked = config.enabled !== false;
                document.getElementById('autoBackupTime').value = config.time || '16:00';
                document.getElementById('autoBackupNamePattern').value = config.name_pattern || 'Auto_Backup_{date}';
                document.getElementById('autoBackupRetention').value = config.retention_days || 7;
            }
        })
        .catch(error => {
            console.error('Error cargando configuración:', error);
            // Usar valores por defecto si hay error
            document.getElementById('autoBackupEnabled').checked = true;
            document.getElementById('autoBackupTime').value = '16:00';
            document.getElementById('autoBackupNamePattern').value = 'Auto_Backup_{date}';
            document.getElementById('autoBackupRetention').value = 7;
        });
}

// Función para guardar la configuración de backups automáticos
function saveAutoBackupConfig() {
    const config = {
        enabled: document.getElementById('autoBackupEnabled').checked,
        time: document.getElementById('autoBackupTime').value,
        name_pattern: document.getElementById('autoBackupNamePattern').value.trim(),
        retention_days: parseInt(document.getElementById('autoBackupRetention').value)
    };
    
    // Validaciones
    if (!config.name_pattern) {
        showError('El patrón de nombre es requerido');
        return;
    }
    
    if (config.retention_days < 1 || config.retention_days > 30) {
        showError('Los días de retención deben estar entre 1 y 30');
        return;
    }
    
    const btn = document.getElementById('saveConfigBtn');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    fetch('/api/backup/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Configuración guardada exitosamente');
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('autoBackupConfigModal'));
            modal.hide();
            // Recargar datos para reflejar cambios
            loadBackupData();
        } else {
            throw new Error(data.message || 'Error al guardar configuración');
        }
    })
    .catch(error => {
        showError('Error al guardar configuración: ' + error.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Función para preparar restauración (llamada desde modal)
function prepareRestore(type, name) {
    // Cerrar modal actual
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    });
    
    // Mostrar confirmación de restauración
    if (confirm(`¿Estás seguro de que deseas restaurar el sistema desde el backup "${name}"? Esta acción sobrescribirá los datos actuales.`)) {
        restoreBackup(type, name);
    }
}

// Función para restaurar backup (ya existente, mantenida para compatibilidad)
function restoreBackup(type, name) {
    showProgressModal('Restaurando sistema...');
    
    // Construir la ruta del backup con extensión .zip
    const backup_path = `backups/${type}/${name}.zip`;
    
    fetch('/api/backup/restore', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            backup_path: backup_path
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProgressModal();
        if (data.success) {
            showSuccess('Sistema restaurado exitosamente');
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            throw new Error(data.message || 'Error al restaurar backup');
        }
    })
    .catch(error => {
        hideProgressModal();
        showError('Error al restaurar backup: ' + error.message);
    });
}

// Función para descargar backup (ya existente, mantenida para compatibilidad)
function downloadBackup(type, name) {
    // Cerrar modal actual
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    });
    
    const url = `/api/backup/download?type=${encodeURIComponent(type)}&name=${encodeURIComponent(name)}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showSuccess('Descarga iniciada');
}

// Función para eliminar backup (ya existente, mantenida para compatibilidad)
function deleteBackup(type, name) {
    if (!confirm(`¿Estás seguro de que deseas eliminar el backup "${name}"?`)) {
        return;
    }
    
    // Construir la ruta del backup con extensión .zip
    const backup_path = `backups/${type}/${name}.zip`;
    
    fetch('/api/backup/delete', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            backup_path: backup_path
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Backup eliminado exitosamente');
            loadBackupData();
        } else {
            throw new Error(data.message || 'Error al eliminar backup');
        }
    })
    .catch(error => {
        showError('Error al eliminar backup: ' + error.message);
    });
}

// Función para cargar datos de backup (ya existente, mantenida para compatibilidad)
function loadBackupData() {
    showLoading(true);
    
    // Cargar métricas y lista de backups en paralelo
    Promise.all([
        fetch('/api/backup/status').then(response => response.json()),
        fetch('/api/backup/list').then(response => response.json())
    ])
    .then(([statusData, listData]) => {
        if (statusData.success) {
            // Actualizar métricas con datos del status
            const metrics = {
                total_backups: (statusData.backup_stats.automatic_count + statusData.backup_stats.manual_count) || 0,
                last_backup: statusData.last_backup ? new Date(statusData.last_backup.last_backup_date).toLocaleString('es-ES') : 'Nunca',
                total_size: statusData.backup_stats.total_size_mb ? `${statusData.backup_stats.total_size_mb.toFixed(2)} MB` : '0 MB',
                last_backup_type: statusData.last_backup && statusData.last_backup.details ? statusData.last_backup.details.backup_type || 'Sistema' : null,
                system_status: statusData.scheduler_status ? (statusData.scheduler_status.running ? 'Activo' : 'Inactivo') : 'Desconocido',
                next_scheduled: statusData.scheduler_status && statusData.scheduler_status.next_run ? new Date(statusData.scheduler_status.next_run).toLocaleString('es-ES') : 'No programado'
            };
            updateBackupMetrics(metrics);
        }
        
        if (listData.success) {
            // Convertir estructura de backups para la tabla
            const allBackups = [];
            
            // Agregar backups automáticos
            if (listData.backups.automatic) {
                listData.backups.automatic.forEach(backup => {
                    allBackups.push({
                        ...backup,
                        type: 'automatic'
                    });
                });
            }
            
            // Agregar backups manuales
            if (listData.backups.manual) {
                listData.backups.manual.forEach(backup => {
                    allBackups.push({
                        ...backup,
                        type: 'manual'
                    });
                });
            }
            
            // Agregar backups importados
            if (listData.backups.imported) {
                listData.backups.imported.forEach(backup => {
                    allBackups.push({
                        ...backup,
                        type: 'imported'
                    });
                });
            }
            
            // Ordenar por fecha de creación (más reciente primero)
            allBackups.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            updateBackupList(allBackups);
        }
        
        if (!statusData.success && !listData.success) {
            throw new Error('Error al cargar datos de backup');
        }
    })
    .catch(error => {
        console.error('Error loading backup data:', error);
        // Mostrar valores por defecto si hay error
        updateBackupMetrics({
            total_backups: 0,
            last_backup: 'Error al cargar',
            total_size: '0 MB'
        });
        updateBackupList([]);
    })
    .finally(() => {
        showLoading(false);
    });
}

// Función para actualizar métricas (ya existente, mantenida para compatibilidad)
function updateBackupMetrics(metrics) {
    if (metrics) {
        // Actualizar total de backups
        const totalBackupsElement = document.getElementById('totalBackups');
        if (totalBackupsElement) {
            totalBackupsElement.textContent = metrics.total_backups || '0';
        }
        
        // Actualizar último backup (usar el ID correcto del HTML)
        const lastBackupElement = document.getElementById('lastBackupTime');
        if (lastBackupElement) {
            lastBackupElement.textContent = metrics.last_backup || 'Nunca';
        }
        
        // Actualizar información de almacenamiento en el elemento existente
        const backupStorageElement = document.getElementById('backupStorage');
        if (backupStorageElement) {
            backupStorageElement.textContent = metrics.total_size || '0 MB';
        }
        
        // Actualizar tipo de último backup si está disponible
        const lastBackupTypeElement = document.getElementById('lastBackupType');
        if (lastBackupTypeElement && metrics.last_backup_type) {
            lastBackupTypeElement.textContent = metrics.last_backup_type;
        }
        
        // Actualizar estado del sistema
        const systemStatusElement = document.getElementById('systemStatus');
        if (systemStatusElement && metrics.system_status) {
            systemStatusElement.textContent = metrics.system_status;
        }
        
        // Actualizar próximo backup programado
        const nextScheduledElement = document.getElementById('nextScheduled');
        if (nextScheduledElement && metrics.next_scheduled) {
            nextScheduledElement.textContent = metrics.next_scheduled;
        }
    }
}

// Función para actualizar lista de backups
function updateBackupList(backups) {
    const container = document.getElementById('backupList');
    const emptyState = document.getElementById('emptyState');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Hide loading spinner
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
    
    if (!backups || backups.length === 0) {
        container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'flex';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    container.innerHTML = backups.map(backup => {
        const typeClass = backup.type === 'automatic' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800';
        const typeText = backup.type === 'automatic' ? 'Automático' : 
                        backup.type === 'manual' ? 'Manual' : 'Importado';
        
        // Formatear fecha
        const formattedDate = backup.created_at ? 
            new Date(backup.created_at).toLocaleString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }) : 'Fecha desconocida';
        
        // Formatear tamaño
        const sizeInMB = backup.size_mb ? parseFloat(backup.size_mb) : 0;
        let formattedSize = '0 MB';
        
        if (sizeInMB > 1024) {
            formattedSize = `${(sizeInMB / 1024).toFixed(2)} GB`;
        } else {
            formattedSize = `${sizeInMB.toFixed(2)} MB`;
        }
        
        return `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 16px;">
                    <div style="font-weight: 500; color: #1f2937; margin-bottom: 4px;">${backup.name || 'Backup sin nombre'}</div>
                    <div style="font-size: 13px; color: #6b7280;">${formattedDate}</div>
                </td>
                <td style="padding: 16px;">
                    <span class="text-xs font-medium px-2.5 py-0.5 rounded-full ${typeClass}">
                        ${typeText}
                    </span>
                </td>
                <td style="padding: 16px; color: #4b5563; font-weight: 500;">
                    ${formattedSize}
                </td>
                <td style="padding: 16px; text-align: right;">
                    <div style="display: flex; gap: 8px; justify-content: flex-end;">
                        <button onclick="downloadBackup('${backup.type}', '${backup.name}')" 
                                class="action-btn" 
                                style="color: #3b82f6;"
                                title="Descargar">
                            <i class="fas fa-download"></i>
                        </button>
                        <button onclick="prepareRestore('${backup.type}', '${backup.name}')" 
                                class="action-btn" 
                                style="color: #10b981;"
                                title="Restaurar">
                            <i class="fas fa-undo"></i>
                        </button>
                        <button onclick="deleteBackup('${backup.type}', '${backup.name}')" 
                                class="action-btn" 
                                style="color: #ef4444;"
                                title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Función para refrescar lista (ya existente, mantenida para compatibilidad)
function refreshBackupList() {
    loadBackupData();
}

// Función para mostrar loading (ya existente, mantenida para compatibilidad)
function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
}

// Función para mostrar modal de progreso (ya existente, mantenida para compatibilidad)
function showProgressModal(message) {
    const modal = document.getElementById('progressModal');
    const messageElement = document.getElementById('progressMessage');
    if (modal && messageElement) {
        messageElement.textContent = message;
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Función para ocultar modal de progreso (ya existente, mantenida para compatibilidad)
function hideProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    }
}

// Función para mostrar modal de importar backup
function showImportBackupModal() {
    // Cerrar modal actual de restauración
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    });
    
    // Crear modal de importación
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'importBackupModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-upload me-2"></i>
                        Importar Backup
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Selecciona un archivo de backup (.zip) para importar al sistema.
                    </div>
                    <div class="mb-3">
                        <label for="backupFile" class="form-label">Archivo de Backup</label>
                        <input type="file" class="form-control" id="backupFile" accept=".zip" required>
                        <div class="form-text">Solo se permiten archivos .zip</div>
                    </div>
                    <div id="uploadProgress" class="progress" style="display: none;">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="uploadBackupFile()" id="uploadBtn">
                        <i class="fas fa-upload me-2"></i>
                        Importar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Agregar modal al DOM y mostrarlo
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Limpiar modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Función para subir archivo de backup
function uploadBackupFile() {
    const fileInput = document.getElementById('backupFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Por favor selecciona un archivo de backup');
        return;
    }
    
    if (!file.name.endsWith('.zip')) {
        showError('Solo se permiten archivos .zip');
        return;
    }
    
    const uploadBtn = document.getElementById('uploadBtn');
    const originalText = uploadBtn.innerHTML;
    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = progressContainer.querySelector('.progress-bar');
    
    // Mostrar progreso
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Subiendo...';
    progressContainer.style.display = 'block';
    
    // Crear FormData
    const formData = new FormData();
    formData.append('backup_file', file);
    
    // Subir archivo
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressBar.textContent = Math.round(percentComplete) + '%';
        }
    });
    
    xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showSuccess('Backup importado exitosamente');
                    // Recargar lista de backups
                    loadBackupData();
                    // Cerrar modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('importBackupModal'));
                    modal.hide();
                } else {
                    showError('Error al importar backup: ' + (response.error || 'Error desconocido'));
                }
            } catch (e) {
                showError('Error al procesar respuesta del servidor');
            }
        } else {
            showError('Error al subir archivo: ' + xhr.status);
        }
        
        // Restaurar botón
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = originalText;
        progressContainer.style.display = 'none';
    });
    
    xhr.addEventListener('error', () => {
        showError('Error de conexión al subir archivo');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = originalText;
        progressContainer.style.display = 'none';
    });
    
    xhr.open('POST', '/api/backup/upload');
    xhr.send(formData);
}

// Función para mostrar modal de eliminar importaciones
function showDeleteImportsModal() {
    // Cerrar modal actual de restauración
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    });
    
    // Obtener lista de backups importados
    fetch('/api/backup/list')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.backups.imported && data.backups.imported.length > 0) {
                const importedBackups = data.backups.imported;
                
                // Crear modal de eliminación
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = 'deleteImportsModal';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-trash me-2"></i>
                                    Eliminar Backups Importados
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="alert alert-warning">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    <strong>Advertencia:</strong> Esta acción eliminará permanentemente los backups seleccionados.
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="selectAllImports">
                                        <label class="form-check-label" for="selectAllImports">
                                            <strong>Seleccionar todos</strong>
                                        </label>
                                    </div>
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead>
                                            <tr>
                                                <th width="50">Seleccionar</th>
                                                <th>Nombre</th>
                                                <th>Fecha de Creación</th>
                                                <th>Tamaño</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${importedBackups.map(backup => {
                                                return `
                                                    <tr>
                                                        <td>
                                                            <div class="form-check">
                                                                <input class="form-check-input import-checkbox" type="checkbox" value="${backup.name}" id="import_${backup.name}">
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <label class="form-check-label" for="import_${backup.name}">
                                                                ${backup.name}
                                                            </label>
                                                        </td>
                                                        <td>${new Date(backup.created_at).toLocaleString()}</td>
                                                        <td>${backup.size}</td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-danger" onclick="deleteSelectedImports()" id="deleteImportsBtn">
                                    <i class="fas fa-trash me-2"></i>
                                    Eliminar Seleccionados
                                </button>
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Agregar modal al DOM y mostrarlo
                document.body.appendChild(modal);
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
                
                // Agregar funcionalidad de seleccionar todos
                const selectAllCheckbox = modal.querySelector('#selectAllImports');
                const importCheckboxes = modal.querySelectorAll('.import-checkbox');
                
                selectAllCheckbox.addEventListener('change', function() {
                    importCheckboxes.forEach(checkbox => {
                        checkbox.checked = this.checked;
                    });
                });
                
                // Limpiar modal cuando se cierre
                modal.addEventListener('hidden.bs.modal', () => {
                    document.body.removeChild(modal);
                });
            } else {
                showError('No hay backups importados para eliminar');
            }
        })
        .catch(error => {
            showError('Error al cargar backups importados: ' + error.message);
        });
}

// Función para eliminar backups importados seleccionados
function deleteSelectedImports() {
    const checkboxes = document.querySelectorAll('.import-checkbox:checked');
    
    if (checkboxes.length === 0) {
        showError('Selecciona al menos un backup para eliminar');
        return;
    }
    
    const selectedBackups = Array.from(checkboxes).map(cb => cb.value);
    
    if (confirm(`¿Estás seguro de que deseas eliminar ${selectedBackups.length} backup(s) importado(s)? Esta acción no se puede deshacer.`)) {
        const deleteBtn = document.getElementById('deleteImportsBtn');
        const originalText = deleteBtn.innerHTML;
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Eliminando...';
        
        // Eliminar backups uno por uno
        Promise.all(selectedBackups.map(backupName => {
            return fetch('/api/backup/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'imported',
                    name: backupName
                })
            }).then(response => response.json());
        }))
        .then(results => {
            const successful = results.filter(r => r.success).length;
            const failed = results.length - successful;
            
            if (successful > 0) {
                showSuccess(`${successful} backup(s) eliminado(s) exitosamente`);
                // Recargar lista de backups
                loadBackupData();
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteImportsModal'));
                modal.hide();
            }
            
            if (failed > 0) {
                showError(`Error al eliminar ${failed} backup(s)`);
            }
        })
        .catch(error => {
            showError('Error al eliminar backups: ' + error.message);
        })
        .finally(() => {
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = originalText;
        });
    }
}

// Cargar datos al inicializar la página
document.addEventListener('DOMContentLoaded', function() {
    loadBackupData();
});