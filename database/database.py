import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# Configuración de la base de datos
DATABASE_PATH = 'pacta_local.db'

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones de base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Crear tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE,
                    password VARCHAR(255),
                    telefono VARCHAR(20),
                    cargo VARCHAR(50),
                    departamento VARCHAR(50),
                    es_admin BOOLEAN DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Crear tabla de clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    tipo_cliente VARCHAR(20) CHECK(tipo_cliente IN ('cliente', 'proveedor')) NOT NULL,
                    rfc VARCHAR(13),
                    direccion TEXT,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    contacto_principal VARCHAR(100),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Crear tabla de contratos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contratos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_contrato VARCHAR(50) UNIQUE NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    usuario_responsable_id INTEGER NOT NULL,
                    persona_responsable_id INTEGER,
                    titulo VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    monto_original DECIMAL(15,2) NOT NULL,
                    monto_actual DECIMAL(15,2) NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    estado VARCHAR(20) CHECK(estado IN ('borrador', 'activo', 'suspendido', 'terminado', 'cancelado')) DEFAULT 'borrador',
                    tipo_contrato VARCHAR(50),
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                    FOREIGN KEY (usuario_responsable_id) REFERENCES usuarios (id),
                    FOREIGN KEY (persona_responsable_id) REFERENCES personas_responsables (id)
                )
            ''')
            
            # Crear tabla de suplementos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suplementos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contrato_id INTEGER NOT NULL,
                    numero_suplemento VARCHAR(50) NOT NULL,
                    tipo_modificacion VARCHAR(50) NOT NULL,
                    descripcion TEXT NOT NULL,
                    monto_modificacion DECIMAL(15,2) DEFAULT 0,
                    fecha_modificacion DATE NOT NULL,
                    usuario_autoriza_id INTEGER NOT NULL,
                    estado VARCHAR(20) CHECK(estado IN ('pendiente', 'aprobado', 'rechazado')) DEFAULT 'pendiente',
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contrato_id) REFERENCES contratos (id),
                    FOREIGN KEY (usuario_autoriza_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Crear tabla de personas responsables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas_responsables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    cargo VARCHAR(100),
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    es_principal BOOLEAN DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )
            ''')
            
            # Crear tabla de documentos de contratos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documentos_contratos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contrato_id INTEGER NOT NULL,
                    nombre_archivo VARCHAR(255) NOT NULL,
                    ruta_archivo VARCHAR(500) NOT NULL,
                    tipo_documento VARCHAR(50) DEFAULT 'PDF',
                    tamaño_archivo INTEGER,
                    fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_subida_id INTEGER NOT NULL,
                    FOREIGN KEY (contrato_id) REFERENCES contratos (id),
                    FOREIGN KEY (usuario_subida_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Crear tabla de actividad del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actividad_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    accion VARCHAR(100) NOT NULL,
                    tabla_afectada VARCHAR(50),
                    registro_id INTEGER,
                    detalles TEXT,
                    fecha_actividad DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Crear tabla de notificaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(50) CHECK(type IN ('system', 'contract_expiring', 'contract_expired', 'user', 'report')) DEFAULT 'system',
                    is_read BOOLEAN DEFAULT 0,
                    contract_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                    FOREIGN KEY (contract_id) REFERENCES contratos (id)
                )
            ''')
            
            # Crear índices para mejorar el rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contratos_cliente ON contratos(cliente_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contratos_usuario ON contratos(usuario_responsable_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_suplementos_contrato ON suplementos(contrato_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actividad_usuario ON actividad_sistema(usuario_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actividad_fecha ON actividad_sistema(fecha_actividad)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones(usuario_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notificaciones_fecha ON notificaciones(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notificaciones_leidas ON notificaciones(usuario_id, is_read)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_personas_cliente ON personas_responsables(cliente_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_personas_principal ON personas_responsables(cliente_id, es_principal)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documentos_contrato ON documentos_contratos(contrato_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documentos_fecha ON documentos_contratos(fecha_subida)')
            
            conn.commit()
            print("Base de datos inicializada correctamente")
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta y retorna los resultados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_insert(self, query, params=None):
        """Ejecuta una inserción y retorna el ID del registro creado"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query, params=None):
        """Ejecuta una actualización y retorna el número de filas afectadas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount

# Instancia global del manejador de base de datos
db_manager = DatabaseManager()