import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from werkzeug.utils import secure_filename
from database.models import DocumentoContrato
from database.database import DatabaseManager

class DocumentService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.base_upload_dir = Path('uploads')
        self.contratos_dir = self.base_upload_dir / 'contratos'
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
        
        # Crear directorios si no existen
        self.base_upload_dir.mkdir(exist_ok=True)
        self.contratos_dir.mkdir(exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """
        Verifica si el archivo tiene una extensión permitida
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_document(self, file, contrato_id: int, tipo_documento: str = 'general', 
                     usuario_id: int = None) -> Dict:
        """
        Guarda un documento asociado a un contrato
        """
        try:
            if not file or not file.filename:
                return {
                    'success': False,
                    'error': 'No se proporcionó ningún archivo'
                }
            
            if not self.allowed_file(file.filename):
                return {
                    'success': False,
                    'error': f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(self.allowed_extensions)}'
                }
            
            # Generar nombre seguro y único
            original_filename = file.filename
            secure_name = secure_filename(original_filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{secure_name}"
            
            # Crear ruta completa
            file_path = self.contratos_dir / unique_filename
            
            # Guardar archivo físico
            file.save(str(file_path))
            
            # Obtener tamaño del archivo
            file_size = file_path.stat().st_size
            
            # Crear registro en base de datos
            documento = DocumentoContrato(
                contrato_id=contrato_id,
                nombre_archivo=original_filename,
                ruta_archivo=str(file_path),
                tipo_documento=tipo_documento,
                tamaño_archivo=file_size,
                usuario_subida_id=usuario_id
            )
            documento.save()
            
            return {
                'success': True,
                'message': 'Documento guardado exitosamente',
                'document_id': documento.id,
                'filename': original_filename,
                'file_path': str(file_path),
                'file_size': file_size
            }
            
        except Exception as e:
            # Limpiar archivo si se creó pero falló el registro en BD
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            
            return {
                'success': False,
                'error': f'Error guardando documento: {str(e)}'
            }
    
    def get_document_info(self, document_id: int) -> Optional[Dict]:
        """
        Obtiene información de un documento por su ID
        """
        try:
            documento = DocumentoContrato.get_by_id(document_id)
            if not documento:
                return None
            
            file_path = Path(documento.ruta_archivo)
            file_exists = file_path.exists()
            
            return {
                'id': documento.id,
                'contrato_id': documento.contrato_id,
                'nombre_archivo': documento.nombre_archivo,
                'ruta_archivo': documento.ruta_archivo,
                'tipo_documento': documento.tipo_documento,
                'tamaño_archivo': documento.tamaño_archivo,
                'fecha_subida': documento.fecha_subida,
                'usuario_subida_id': documento.usuario_subida_id,
                'file_exists': file_exists
            }
            
        except Exception as e:
            return None
    
    def delete_document(self, document_id: int, delete_file: bool = True) -> Dict:
        """
        Elimina un documento del sistema
        """
        try:
            documento = DocumentoContrato.get_by_id(document_id)
            if not documento:
                return {
                    'success': False,
                    'error': 'Documento no encontrado'
                }
            
            file_path = Path(documento.ruta_archivo)
            
            # Eliminar registro de base de datos
            documento.delete()
            
            # Eliminar archivo físico si se solicita y existe
            if delete_file and file_path.exists():
                file_path.unlink()
            
            return {
                'success': True,
                'message': 'Documento eliminado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error eliminando documento: {str(e)}'
            }
    
    def get_documents_by_contract(self, contrato_id: int) -> List[Dict]:
        """
        Obtiene todos los documentos de un contrato
        """
        try:
            documentos = DocumentoContrato.get_by_contrato(contrato_id)
            result = []
            
            for doc in documentos:
                file_path = Path(doc.ruta_archivo)
                result.append({
                    'id': doc.id,
                    'contrato_id': doc.contrato_id,
                    'nombre_archivo': doc.nombre_archivo,
                    'ruta_archivo': doc.ruta_archivo,
                    'tipo_documento': doc.tipo_documento,
                    'tamaño_archivo': doc.tamaño_archivo,
                    'fecha_subida': doc.fecha_subida,
                    'usuario_subida_id': doc.usuario_subida_id,
                    'file_exists': file_path.exists()
                })
            
            return result
            
        except Exception as e:
            return []
    
    def get_all_documents(self) -> List[Dict]:
        """
        Obtiene información de todos los documentos en el sistema
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT d.*, c.titulo as contrato_titulo
                    FROM documentos_contratos d
                    LEFT JOIN contratos c ON d.contrato_id = c.id
                    ORDER BY d.fecha_subida DESC
                """)
                
                results = cursor.fetchall()
                documents = []
                
                for row in results:
                    file_path = Path(row['ruta_archivo'])
                    documents.append({
                        'id': row['id'],
                        'contrato_id': row['contrato_id'],
                        'contrato_titulo': row['contrato_titulo'],
                        'nombre_archivo': row['nombre_archivo'],
                        'ruta_archivo': row['ruta_archivo'],
                        'tipo_documento': row['tipo_documento'],
                        'tamaño_archivo': row['tamaño_archivo'],
                        'fecha_subida': row['fecha_subida'],
                        'usuario_subida_id': row['usuario_subida_id'],
                        'file_exists': file_path.exists()
                    })
                
                return documents
                
        except Exception as e:
            return []
    
    def get_storage_stats(self) -> Dict:
        """
        Obtiene estadísticas de almacenamiento de documentos
        """
        try:
            stats = {
                'total_documents': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'documents_by_type': {},
                'missing_files': 0
            }
            
            documents = self.get_all_documents()
            stats['total_documents'] = len(documents)
            
            for doc in documents:
                # Contar por tipo
                tipo = doc['tipo_documento'] or 'sin_tipo'
                if tipo not in stats['documents_by_type']:
                    stats['documents_by_type'][tipo] = 0
                stats['documents_by_type'][tipo] += 1
                
                # Sumar tamaño si el archivo existe
                if doc['file_exists'] and doc['tamaño_archivo']:
                    stats['total_size_bytes'] += doc['tamaño_archivo']
                elif not doc['file_exists']:
                    stats['missing_files'] += 1
            
            stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            return {
                'error': str(e),
                'total_documents': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'documents_by_type': {},
                'missing_files': 0
            }
    
    def cleanup_orphaned_files(self) -> Dict:
        """
        Limpia archivos huérfanos (archivos físicos sin registro en BD)
        """
        try:
            if not self.contratos_dir.exists():
                return {
                    'success': True,
                    'message': 'Directorio de contratos no existe',
                    'files_removed': 0
                }
            
            # Obtener todos los archivos registrados en BD
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ruta_archivo FROM documentos_contratos")
                registered_files = {Path(row['ruta_archivo']) for row in cursor.fetchall()}
            
            # Buscar archivos físicos
            physical_files = set(self.contratos_dir.rglob('*'))
            physical_files = {f for f in physical_files if f.is_file()}
            
            # Encontrar archivos huérfanos
            orphaned_files = physical_files - registered_files
            
            # Eliminar archivos huérfanos
            removed_count = 0
            for file_path in orphaned_files:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception:
                    pass  # Continuar con el siguiente archivo
            
            return {
                'success': True,
                'message': f'Limpieza completada. Se eliminaron {removed_count} archivos huérfanos',
                'files_removed': removed_count,
                'total_physical_files': len(physical_files),
                'total_registered_files': len(registered_files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en limpieza de archivos: {str(e)}',
                'files_removed': 0
            }