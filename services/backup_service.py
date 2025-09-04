import os
import sqlite3
import zipfile
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from database.database import DatabaseManager

class BackupService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.backup_dir = Path('backups')
        self.uploads_dir = Path('uploads')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorios para diferentes tipos de backup
        (self.backup_dir / 'automatic').mkdir(exist_ok=True)
        (self.backup_dir / 'manual').mkdir(exist_ok=True)
    
    def create_backup(self, backup_type: str = 'manual', reason: str = '', custom_name: str = None) -> Dict:
        """
        Crea un backup completo de la aplicación
        
        Args:
            backup_type: 'automatic' o 'manual'
            reason: Razón del backup (para logs)
            custom_name: Nombre personalizado para el backup (opcional)
        
        Returns:
            Dict con información del backup creado
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Usar nombre personalizado si se proporciona, sino usar formato por defecto
            if custom_name and custom_name.strip():
                # Limpiar el nombre personalizado (remover caracteres no válidos)
                clean_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).strip()
                clean_name = clean_name.replace(' ', '_')
                backup_name = f"{clean_name}_{timestamp}"
            else:
                backup_name = f"pacta_backup_{backup_type}_{timestamp}"
            
            backup_subdir = self.backup_dir / backup_type
            backup_path = backup_subdir / f"{backup_name}.zip"
            
            # Crear directorio temporal para el backup
            temp_dir = Path(f"temp_backup_{timestamp}")
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # 1. Crear backup de la base de datos
                db_backup_path = self._backup_database(temp_dir)
                
                # 2. Copiar archivos de uploads si existen
                uploads_backup_path = self._backup_uploads(temp_dir)
                
                # 3. Crear metadata del backup
                metadata = self._create_backup_metadata(backup_type, reason, timestamp)
                metadata_path = temp_dir / 'backup_metadata.json'
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # 4. Comprimir todo en un archivo ZIP
                self._create_zip_backup(temp_dir, backup_path)
                
                # 5. Limpiar directorio temporal
                shutil.rmtree(temp_dir)
                
                # 6. Registrar el backup en el sistema
                backup_info = {
                    'name': backup_name,
                    'path': str(backup_path),
                    'type': backup_type,
                    'size': backup_path.stat().st_size,
                    'created_at': datetime.now().isoformat(),
                    'reason': reason,
                    'metadata': metadata
                }
                
                self._log_backup_activity(backup_info)
                
                return {
                    'success': True,
                    'backup_info': backup_info,
                    'message': f'Backup {backup_type} creado exitosamente'
                }
                
            except Exception as e:
                # Limpiar en caso de error
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                raise e
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error al crear backup: {str(e)}'
            }
    
    def _backup_database(self, temp_dir: Path) -> Path:
        """
        Crea una copia de la base de datos SQLite
        """
        db_backup_path = temp_dir / 'pacta_local.db'
        
        # Usar el comando VACUUM INTO para crear una copia limpia
        with self.db_manager.get_connection() as conn:
            conn.execute(f"VACUUM INTO '{db_backup_path}'")
        
        return db_backup_path
    
    def _backup_uploads(self, temp_dir: Path) -> Optional[Path]:
        """
        Copia todos los archivos de uploads
        """
        if not self.uploads_dir.exists():
            return None
        
        uploads_backup_path = temp_dir / 'uploads'
        shutil.copytree(self.uploads_dir, uploads_backup_path)
        
        return uploads_backup_path
    
    def _create_backup_metadata(self, backup_type: str, reason: str, timestamp: str) -> Dict:
        """
        Crea metadata del backup con estadísticas de la BD
        """
        metadata = {
            'backup_type': backup_type,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'reason': reason,
            'version': '1.0',
            'database_stats': self._get_database_stats()
        }
        
        return metadata
    
    def _get_database_stats(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos
        """
        stats = {}
        tables = ['usuarios', 'clientes', 'contratos', 'suplementos', 
                 'personas_responsables', 'documentos_contratos', 
                 'actividad_sistema', 'notificaciones']
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                except sqlite3.OperationalError:
                    stats[table] = 0
        
        return stats
    
    def _create_zip_backup(self, source_dir: Path, zip_path: Path):
        """
        Crea un archivo ZIP comprimido con todos los archivos del backup
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
    
    def _log_backup_activity(self, backup_info: Dict):
        """
        Registra la actividad de backup en el sistema
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO actividad_sistema 
                (usuario_id, accion, tabla_afectada, detalles, fecha_actividad)
                VALUES (?, ?, ?, ?, ?)
            """, (
                None,  # Sistema automático
                f'BACKUP_{backup_info["type"].upper()}',
                'sistema',
                json.dumps({
                    'backup_name': backup_info['name'],
                    'size_bytes': backup_info['size'],
                    'reason': backup_info['reason']
                }),
                datetime.now()
            ))
            conn.commit()
    
    def list_backups(self) -> Dict:
        """
        Lista todos los backups disponibles
        """
        try:
            backups = {
                'automatic': [],
                'manual': [],
                'imported': []
            }
            
            for backup_type in ['automatic', 'manual', 'imported']:
                backup_subdir = self.backup_dir / backup_type
                if backup_subdir.exists():
                    for backup_file in backup_subdir.glob('*.zip'):
                        backup_info = self._get_backup_info(backup_file)
                        if backup_info:
                            backups[backup_type].append(backup_info)
            
            # Ordenar por fecha de creación (más reciente primero)
            for backup_type in backups:
                backups[backup_type].sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'success': True,
                'backups': backups
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_backup_info(self, backup_path: Path) -> Optional[Dict]:
        """
        Obtiene información de un archivo de backup
        """
        try:
            stat = backup_path.stat()
            
            # Intentar leer metadata del ZIP
            metadata = None
            try:
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_metadata.json' in zipf.namelist():
                        with zipf.open('backup_metadata.json') as f:
                            metadata = json.load(f)
            except:
                pass
            
            return {
                'name': backup_path.stem,
                'path': str(backup_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'metadata': metadata
            }
            
        except Exception:
            return None
    
    def cleanup_old_backups(self, retention_days: int = 7, keep_minimum: int = 3) -> Dict:
        """
        Elimina backups automáticos obsoletos según política de retención
        Mantiene todos los backups manuales
        
        Args:
            retention_days: Días de retención para backups automáticos
            keep_minimum: Número mínimo de backups automáticos a mantener
        """
        try:
            deleted_count = 0
            kept_count = 0
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            automatic_dir = self.backup_dir / 'automatic'
            if not automatic_dir.exists():
                return {
                    'success': True,
                    'deleted_count': 0,
                    'kept_count': 0,
                    'message': 'No hay directorio de backups automáticos'
                }
            
            # Obtener todos los backups automáticos ordenados por fecha (más reciente primero)
            backup_files = []
            for backup_file in automatic_dir.glob('*.zip'):
                file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
                backup_files.append((backup_file, file_date))
            
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Mantener siempre los backups más recientes (keep_minimum)
            for i, (backup_file, file_date) in enumerate(backup_files):
                if i < keep_minimum:
                    # Mantener los más recientes
                    kept_count += 1
                elif file_date < cutoff_date:
                    # Eliminar los que superan la fecha de retención
                    backup_file.unlink()
                    deleted_count += 1
                else:
                    # Mantener los que están dentro del período de retención
                    kept_count += 1
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'kept_count': kept_count,
                'retention_days': retention_days,
                'keep_minimum': keep_minimum,
                'message': f'Política de retención aplicada: {deleted_count} eliminados, {kept_count} mantenidos'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_backup(self, backup_path: str) -> Dict:
        """
        Elimina un backup específico
        """
        try:
            backup_file = Path(backup_path)
            if backup_file.exists() and backup_file.suffix == '.zip':
                backup_file.unlink()
                return {
                    'success': True,
                    'message': 'Backup eliminado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'Archivo de backup no encontrado'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }