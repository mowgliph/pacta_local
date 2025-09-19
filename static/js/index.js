/**
 * PACTA - Punto de entrada principal de JavaScript
 * Este archivo importa y organiza todos los scripts de la aplicación
 */

// ===== UTILIDADES DEL SISTEMA =====
import './toast_manager.js';
import './confirm_modal.js';
import './user_avatar.js';

// ===== COMPONENTES PRINCIPALES =====
import './sidebar_functions.js';
import './notification_functions.js';

// ===== MÓDULOS DE FUNCIONALIDAD =====
// Módulo de Dashboard
import './dashboard_functions.js';

// Módulo de Usuarios
import './user_functions.js';

// Módulo de Contratos
import './contract_functions.js';

// Módulo de Personas
import './personas.js';

// Módulo de Proveedores
import './proveedores.js';

// Módulo de Clientes
import './clientes.js';

// Módulo de Suplementos
import './suplementos.js';

// Módulo de Reportes
import './report_functions.js';

// Módulo de Copias de Seguridad
import './backup_functions.js';

// Módulo de relación Proveedores-Clientes
import './providers-clients-block.js';

console.log('PACTA - Todos los módulos JavaScript han sido cargados correctamente');
