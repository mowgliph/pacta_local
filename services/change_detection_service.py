import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database.database import DatabaseManager

class ChangeDetectionService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self._ensure_change_tracking_table()
    
    def _ensure_change_tracking_table(self):
        """
        Crea la tabla para rastrear cambios si no existe
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS change_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    record_id INTEGER,
                    change_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    backup_processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Crear índices para mejorar el rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_change_tracking_table 
                ON change_tracking(table_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_change_tracking_timestamp 
                ON change_tracking(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_change_tracking_processed 
                ON change_tracking(backup_processed)
            """)
            
            conn.commit()
    
    def record_change(self, table_name: str, operation: str, record_id: Optional[int] = None, 
                     change_data: Optional[Dict] = None):
        """
        Registra un cambio en el sistema
        
        Args:
            table_name: Nombre de la tabla afectada
            operation: Tipo de operación (INSERT, UPDATE, DELETE)
            record_id: ID del registro afectado
            change_data: Datos adicionales del cambio
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO change_tracking 
                    (table_name, operation, record_id, change_data, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    table_name,
                    operation,
                    record_id,
                    json.dumps(change_data) if change_data else None,
                    datetime.now()
                ))
                conn.commit()
        except Exception as e:
            print(f"Error registrando cambio: {e}")
    
    def has_changes_since_last_backup(self) -> Dict:
        """
        Verifica si hay cambios relevantes desde el último backup
        
        Returns:
            Dict con información sobre cambios pendientes
        """
        try:
            # Tablas que requieren backup cuando cambian
            relevant_tables = ['usuarios', 'clientes', 'contratos', 'suplementos', 
                             'personas_responsables', 'documentos_contratos']
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar cambios no procesados en tablas relevantes
                placeholders = ','.join(['?' for _ in relevant_tables])
                cursor.execute(f"""
                    SELECT table_name, operation, COUNT(*) as change_count,
                           MIN(timestamp) as first_change,
                           MAX(timestamp) as last_change
                    FROM change_tracking 
                    WHERE table_name IN ({placeholders})
                    AND backup_processed = FALSE
                    GROUP BY table_name, operation
                    ORDER BY last_change DESC
                """, relevant_tables)
                
                changes = cursor.fetchall()
                
                if not changes:
                    return {
                        'has_changes': False,
                        'changes': [],
                        'total_changes': 0,
                        'message': 'No hay cambios pendientes de backup'
                    }
                
                # Formatear los cambios
                formatted_changes = []
                total_changes = 0
                
                for change in changes:
                    table_name, operation, count, first_change, last_change = change
                    formatted_changes.append({
                        'table': table_name,
                        'operation': operation,
                        'count': count,
                        'first_change': first_change,
                        'last_change': last_change
                    })
                    total_changes += count
                
                return {
                    'has_changes': True,
                    'changes': formatted_changes,
                    'total_changes': total_changes,
                    'message': f'Se encontraron {total_changes} cambios pendientes de backup'
                }
                
        except Exception as e:
            return {
                'has_changes': False,
                'error': str(e),
                'message': f'Error verificando cambios: {str(e)}'
            }
    
    def mark_changes_as_processed(self) -> Dict:
        """
        Marca todos los cambios pendientes como procesados después de un backup
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Contar cambios antes de marcarlos
                cursor.execute("""
                    SELECT COUNT(*) FROM change_tracking 
                    WHERE backup_processed = FALSE
                """)
                pending_count = cursor.fetchone()[0]
                
                # Marcar como procesados
                cursor.execute("""
                    UPDATE change_tracking 
                    SET backup_processed = TRUE 
                    WHERE backup_processed = FALSE
                """)
                
                conn.commit()
                
                return {
                    'success': True,
                    'processed_count': pending_count,
                    'message': f'Se marcaron {pending_count} cambios como procesados'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_change_summary(self, days: int = 7) -> Dict:
        """
        Obtiene un resumen de cambios en los últimos días
        
        Args:
            days: Número de días hacia atrás para el resumen
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        table_name,
                        operation,
                        COUNT(*) as count,
                        DATE(timestamp) as change_date
                    FROM change_tracking 
                    WHERE timestamp >= ?
                    GROUP BY table_name, operation, DATE(timestamp)
                    ORDER BY change_date DESC, table_name, operation
                """, (cutoff_date,))
                
                changes = cursor.fetchall()
                
                # Organizar por fecha
                summary_by_date = {}
                total_changes = 0
                
                for change in changes:
                    table_name, operation, count, change_date = change
                    
                    if change_date not in summary_by_date:
                        summary_by_date[change_date] = []
                    
                    summary_by_date[change_date].append({
                        'table': table_name,
                        'operation': operation,
                        'count': count
                    })
                    
                    total_changes += count
                
                return {
                    'success': True,
                    'summary': summary_by_date,
                    'total_changes': total_changes,
                    'period_days': days
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_changes(self, days: int = 30) -> Dict:
        """
        Limpia registros de cambios antiguos para mantener la tabla optimizada
        
        Args:
            days: Días de antigüedad para eliminar registros
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Contar registros a eliminar
                cursor.execute("""
                    SELECT COUNT(*) FROM change_tracking 
                    WHERE timestamp < ? AND backup_processed = TRUE
                """, (cutoff_date,))
                
                count_to_delete = cursor.fetchone()[0]
                
                # Eliminar registros antiguos ya procesados
                cursor.execute("""
                    DELETE FROM change_tracking 
                    WHERE timestamp < ? AND backup_processed = TRUE
                """, (cutoff_date,))
                
                conn.commit()
                
                return {
                    'success': True,
                    'deleted_count': count_to_delete,
                    'message': f'Se eliminaron {count_to_delete} registros de cambios antiguos'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_last_backup_info(self) -> Optional[Dict]:
        """
        Obtiene información del último backup realizado
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT fecha_actividad, detalles 
                    FROM actividad_sistema 
                    WHERE accion LIKE 'BACKUP_%'
                    ORDER BY fecha_actividad DESC 
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                
                if result:
                    fecha_actividad, detalles = result
                    try:
                        detalles_json = json.loads(detalles) if detalles else {}
                    except:
                        detalles_json = {}
                    
                    return {
                        'last_backup_date': fecha_actividad,
                        'details': detalles_json
                    }
                
                return None
                
        except Exception as e:
            print(f"Error obteniendo información del último backup: {e}")
            return None

# Funciones auxiliares para integrar con las operaciones de BD existentes
def track_user_change(operation: str, user_id: Optional[int] = None, user_data: Optional[Dict] = None):
    """
    Función auxiliar para rastrear cambios en usuarios
    """
    service = ChangeDetectionService()
    service.record_change('usuarios', operation, user_id, user_data)

def track_contract_change(operation: str, contract_id: Optional[int] = None, contract_data: Optional[Dict] = None):
    """
    Función auxiliar para rastrear cambios en contratos
    """
    service = ChangeDetectionService()
    service.record_change('contratos', operation, contract_id, contract_data)

def track_supplement_change(operation: str, supplement_id: Optional[int] = None, supplement_data: Optional[Dict] = None):
    """
    Función auxiliar para rastrear cambios en suplementos
    """
    service = ChangeDetectionService()
    service.record_change('suplementos', operation, supplement_id, supplement_data)

def track_client_change(operation: str, client_id: Optional[int] = None, client_data: Optional[Dict] = None):
    """
    Función auxiliar para rastrear cambios en clientes
    """
    service = ChangeDetectionService()
    service.record_change('clientes', operation, client_id, client_data)

def track_document_change(operation: str, document_id: Optional[int] = None, document_data: Optional[Dict] = None):
    """
    Función auxiliar para rastrear cambios en documentos
    """
    service = ChangeDetectionService()
    service.record_change('documentos_contratos', operation, document_id, document_data)