import os
import sqlite3
import zipfile
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from database.database import DatabaseManager

class RestoreService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.backup_dir = Path('backups')
        self.uploads_dir = Path('uploads')
        self.temp_restore_dir = Path('temp_restore')
    
    def list_available_backups(self) -> Dict:
        """
        Lista todos los backups disponibles para restauración
        """
        try:
            backups = []
            
            for backup_type in ['automatic', 'manual']:
                backup_subdir = self.backup_dir / backup_type
                if backup_subdir.exists():
                    for backup_file in backup_subdir.glob('*.zip'):
                        backup_info = self._get_backup_details(backup_file, backup_type)
                        if backup_info:
                            backups.append(backup_info)
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'success': True,
                'backups': backups,
                'total_count': len(backups)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error listando backups: {str(e)}'
            }
    
    def _get_backup_details(self, backup_path: Path, backup_type: str) -> Optional[Dict]:
        """
        Obtiene detalles completos de un backup
        """
        try:
            stat = backup_path.stat()
            
            # Leer metadata del backup
            metadata = None
            database_stats = None
            
            try:
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_metadata.json' in zipf.namelist():
                        with zipf.open('backup_metadata.json') as f:
                            metadata = json.load(f)
                            database_stats = metadata.get('database_stats', {})
            except Exception as e:
                print(f"Error leyendo metadata de {backup_path}: {e}")
            
            return {
                'name': backup_path.stem,
                'path': str(backup_path),
                'type': backup_type,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'metadata': metadata,
                'database_stats': database_stats,
                'has_uploads': self._backup_has_uploads(backup_path)
            }
            
        except Exception as e:
            print(f"Error obteniendo detalles de backup {backup_path}: {e}")
            return None
    
    def _backup_has_uploads(self, backup_path: Path) -> bool:
        """
        Verifica si el backup contiene archivos de uploads
        """
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                return any(name.startswith('uploads/') for name in zipf.namelist())
        except:
            return False
    
    def validate_backup(self, backup_path: str) -> Dict:
        """
        Valida la integridad de un archivo de backup
        
        Args:
            backup_path: Ruta al archivo de backup
        
        Returns:
            Dict con resultado de la validación
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                return {
                    'valid': False,
                    'error': 'Archivo de backup no encontrado'
                }
            
            if backup_file.suffix != '.zip':
                return {
                    'valid': False,
                    'error': 'El archivo no es un backup válido (.zip)'
                }
            
            # Verificar que el ZIP no esté corrupto
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Verificar integridad del ZIP
                    bad_file = zipf.testzip()
                    if bad_file:
                        return {
                            'valid': False,
                            'error': f'Archivo corrupto en el backup: {bad_file}'
                        }
                    
                    # Verificar archivos esenciales
                    files_in_zip = zipf.namelist()
                    
                    if 'pacta_local.db' not in files_in_zip:
                        return {
                            'valid': False,
                            'error': 'El backup no contiene la base de datos'
                        }
                    
                    if 'backup_metadata.json' not in files_in_zip:
                        return {
                            'valid': False,
                            'error': 'El backup no contiene metadata válida'
                        }
                    
                    # Verificar metadata
                    try:
                        with zipf.open('backup_metadata.json') as f:
                            metadata = json.load(f)
                            
                        if not isinstance(metadata, dict):
                            return {
                                'valid': False,
                                'error': 'Metadata del backup inválida'
                            }
                            
                    except Exception as e:
                        return {
                            'valid': False,
                            'error': f'Error leyendo metadata: {str(e)}'
                        }
            
            except zipfile.BadZipFile:
                return {
                    'valid': False,
                    'error': 'El archivo ZIP está corrupto'
                }
            
            return {
                'valid': True,
                'message': 'Backup válido y listo para restaurar'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def restore_from_backup(self, backup_path: str, restore_options: Optional[Dict] = None) -> Dict:
        """
        Restaura la aplicación desde un archivo de backup
        
        Args:
            backup_path: Ruta al archivo de backup
            restore_options: Opciones de restauración
                - restore_database: bool (default: True)
                - restore_uploads: bool (default: True)
                - backup_current: bool (default: True)
        
        Returns:
            Dict con resultado de la restauración
        """
        print(f"[RESTORE] Iniciando restauración desde: {backup_path}")
        
        # Opciones por defecto
        if restore_options is None:
            restore_options = {}
        
        restore_database = restore_options.get('restore_database', True)
        restore_uploads = restore_options.get('restore_uploads', True)
        backup_current = restore_options.get('backup_current', True)
        
        print(f"[RESTORE] Opciones: database={restore_database}, uploads={restore_uploads}, backup_current={backup_current}")
        
        try:
            print(f"[RESTORE] Validando backup...")
            # Validar backup antes de proceder
            validation = self.validate_backup(backup_path)
            if not validation.get('valid', False):
                print(f"[RESTORE] Error en validación: {validation.get('error')}")
                return {
                    'success': False,
                    'error': validation.get('error', 'Backup inválido')
                }
            
            print(f"[RESTORE] Backup validado correctamente")
            backup_file = Path(backup_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Crear backup de seguridad del estado actual si se solicita
            current_backup_info = None
            if backup_current:
                print(f"[RESTORE] Creando backup de seguridad del estado actual...")
                from services.backup_service import BackupService
                backup_service = BackupService()
                current_backup_result = backup_service.create_backup(
                    backup_type='manual',
                    reason=f'Backup automático antes de restauración desde {backup_file.name}'
                )
                
                if current_backup_result.get('success', False):
                    current_backup_info = current_backup_result['backup_info']
                    print(f"[RESTORE] Backup de seguridad creado: {current_backup_info['name']}")
                else:
                    print(f"[RESTORE] Error creando backup de seguridad: {current_backup_result.get('error')}")
                    return {
                        'success': False,
                        'error': 'No se pudo crear backup de seguridad del estado actual',
                        'details': current_backup_result.get('error', '')
                    }
            
            # Crear directorio temporal para la restauración
            print(f"[RESTORE] Preparando directorio temporal...")
            if self.temp_restore_dir.exists():
                shutil.rmtree(self.temp_restore_dir)
            self.temp_restore_dir.mkdir()
            
            try:
                # Extraer el backup
                print(f"[RESTORE] Extrayendo backup...")
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(self.temp_restore_dir)
                print(f"[RESTORE] Backup extraído correctamente")
                
                # Leer metadata
                print(f"[RESTORE] Leyendo metadata...")
                metadata_path = self.temp_restore_dir / 'backup_metadata.json'
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"[RESTORE] Metadata leída correctamente")
                
                restore_results = []
                
                # Restaurar base de datos
                if restore_database:
                    print(f"[RESTORE] Iniciando restauración de base de datos...")
                    db_result = self._restore_database()
                    restore_results.append(('database', db_result))
                    print(f"[RESTORE] Resultado restauración BD: {db_result.get('success', False)}")
                    
                    if not db_result.get('success', False):
                        print(f"[RESTORE] Error en restauración BD: {db_result.get('error', '')}")
                        raise Exception(f"Error restaurando base de datos: {db_result.get('error', '')}")
                
                # Restaurar archivos de uploads
                if restore_uploads:
                    print(f"[RESTORE] Iniciando restauración de uploads...")
                    uploads_result = self._restore_uploads()
                    restore_results.append(('uploads', uploads_result))
                    print(f"[RESTORE] Resultado restauración uploads: {uploads_result.get('success', False)}")
                    
                    if not uploads_result.get('success', False):
                        print(f"Advertencia restaurando uploads: {uploads_result.get('error', '')}")
                
                # Limpiar directorio temporal
                print(f"[RESTORE] Limpiando directorio temporal...")
                shutil.rmtree(self.temp_restore_dir)
                
                # Registrar la restauración en el sistema
                self._log_restore_activity(backup_file.name, metadata, restore_results)
                
                return {
                    'success': True,
                    'message': 'Restauración completada exitosamente',
                    'backup_name': backup_file.name,
                    'restore_timestamp': timestamp,
                    'current_backup_info': current_backup_info,
                    'metadata': metadata,
                    'restore_results': restore_results
                }
                
            except Exception as e:
                # Limpiar en caso de error
                if self.temp_restore_dir.exists():
                    shutil.rmtree(self.temp_restore_dir)
                raise e
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error durante la restauración: {str(e)}'
            }
    
    def _restore_database(self) -> Dict:
        """
        Restaura la base de datos desde el backup
        """
        try:
            print(f"[RESTORE_DB] Iniciando restauración de base de datos...")
            backup_db_path = self.temp_restore_dir / 'pacta_local.db'
            current_db_path = Path('pacta_local.db')
            
            print(f"[RESTORE_DB] Verificando archivo de BD en backup: {backup_db_path}")
            if not backup_db_path.exists():
                print(f"[RESTORE_DB] Error: BD no encontrada en {backup_db_path}")
                return {
                    'success': False,
                    'error': 'Base de datos no encontrada en el backup'
                }
            
            print(f"[RESTORE_DB] Preparando para restaurar BD...")
            
            # Crear backup temporal de la BD actual
            print(f"[RESTORE_DB] Creando backup temporal de BD actual...")
            if current_db_path.exists():
                temp_current_db = Path(f'pacta_local_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                shutil.copy2(current_db_path, temp_current_db)
                print(f"[RESTORE_DB] Backup temporal creado: {temp_current_db}")
            
            try:
                # Reemplazar la base de datos actual
                print(f"[RESTORE_DB] Reemplazando base de datos actual...")
                if current_db_path.exists():
                    current_db_path.unlink()
                    print(f"[RESTORE_DB] BD actual eliminada")
                
                shutil.copy2(backup_db_path, current_db_path)
                print(f"[RESTORE_DB] BD del backup copiada")
                
                # Verificar que la BD restaurada funciona
                print(f"[RESTORE_DB] Verificando BD restaurada...")
                test_conn = sqlite3.connect(current_db_path)
                result = test_conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()
                test_conn.close()
                print(f"[RESTORE_DB] BD verificada - usuarios encontrados: {result[0] if result else 0}")
                
                # Reinicializar el DatabaseManager
                print(f"[RESTORE_DB] Reinicializando DatabaseManager...")
                self.db_manager = DatabaseManager()
                print(f"[RESTORE_DB] DatabaseManager reinicializado")
                
                # Eliminar backup temporal si todo salió bien
                if 'temp_current_db' in locals() and temp_current_db.exists():
                    temp_current_db.unlink()
                    print(f"[RESTORE_DB] Backup temporal eliminado")
                
                print(f"[RESTORE_DB] Restauración de BD completada exitosamente")
                return {
                    'success': True,
                    'message': 'Base de datos restaurada exitosamente'
                }
                
            except Exception as e:
                # Restaurar BD original en caso de error
                if 'temp_current_db' in locals() and temp_current_db.exists():
                    if current_db_path.exists():
                        current_db_path.unlink()
                    shutil.copy2(temp_current_db, current_db_path)
                    temp_current_db.unlink()
                
                raise e
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_uploads(self) -> Dict:
        """
        Restaura los archivos de uploads desde el backup
        """
        try:
            backup_uploads_path = self.temp_restore_dir / 'uploads'
            
            if not backup_uploads_path.exists():
                return {
                    'success': True,
                    'message': 'No hay archivos de uploads en el backup'
                }
            
            # Crear backup de uploads actuales si existen
            if self.uploads_dir.exists():
                temp_uploads_backup = Path(f'uploads_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copytree(self.uploads_dir, temp_uploads_backup)
            
            try:
                # Eliminar uploads actuales
                if self.uploads_dir.exists():
                    shutil.rmtree(self.uploads_dir)
                
                # Restaurar uploads desde backup
                shutil.copytree(backup_uploads_path, self.uploads_dir)
                
                # Eliminar backup temporal si todo salió bien
                if 'temp_uploads_backup' in locals() and temp_uploads_backup.exists():
                    shutil.rmtree(temp_uploads_backup)
                
                # Contar archivos restaurados
                file_count = sum(1 for _ in self.uploads_dir.rglob('*') if _.is_file())
                
                return {
                    'success': True,
                    'message': f'Se restauraron {file_count} archivos de uploads'
                }
                
            except Exception as e:
                # Restaurar uploads originales en caso de error
                if 'temp_uploads_backup' in locals() and temp_uploads_backup.exists():
                    if self.uploads_dir.exists():
                        shutil.rmtree(self.uploads_dir)
                    shutil.copytree(temp_uploads_backup, self.uploads_dir)
                    shutil.rmtree(temp_uploads_backup)
                
                raise e
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_restore_activity(self, backup_name: str, metadata: Dict, restore_results: List):
        """
        Registra la actividad de restauración en el sistema
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO actividad_sistema 
                    (usuario_id, accion, tabla_afectada, detalles, fecha_actividad)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    None,  # Sistema automático
                    'RESTORE',
                    'sistema',
                    json.dumps({
                        'backup_name': backup_name,
                        'backup_metadata': metadata,
                        'restore_results': restore_results
                    }),
                    datetime.now()
                ))
                conn.commit()
        except Exception as e:
            print(f"Error registrando actividad de restauración: {e}")
    
    def get_restore_history(self, limit: int = 10) -> Dict:
        """
        Obtiene el historial de restauraciones
        
        Args:
            limit: Número máximo de registros a devolver
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha_actividad, detalles 
                    FROM actividad_sistema 
                    WHERE accion = 'RESTORE'
                    ORDER BY fecha_actividad DESC 
                    LIMIT ?
                """, (limit,))
                
                results = cursor.fetchall()
                
                history = []
                for fecha_actividad, detalles in results:
                    try:
                        detalles_json = json.loads(detalles) if detalles else {}
                    except:
                        detalles_json = {}
                    
                    history.append({
                        'date': fecha_actividad,
                        'details': detalles_json
                    })
                
                return {
                    'success': True,
                    'history': history
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }