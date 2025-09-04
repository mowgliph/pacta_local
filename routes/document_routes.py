from flask import Blueprint, request, jsonify, send_file, session
from functools import wraps
from services.document_service import DocumentService
from database.models import DocumentoContrato
import os

# Decorador para requerir login (simplificado)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Acceso no autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')
document_service = DocumentService()

@document_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """
    API para subir un documento
    """
    try:
        # Validar parámetros requeridos
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se proporcionó ningún archivo'
            }), 400
        
        file = request.files['file']
        contrato_id = request.form.get('contrato_id')
        tipo_documento = request.form.get('tipo_documento', 'general')
        usuario_id = session.get('user_id')
        
        if not contrato_id:
            return jsonify({
                'success': False,
                'error': 'ID de contrato requerido'
            }), 400
        
        try:
            contrato_id = int(contrato_id)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'ID de contrato inválido'
            }), 400
        
        # Guardar documento
        result = document_service.save_document(
            file=file,
            contrato_id=contrato_id,
            tipo_documento=tipo_documento,
            usuario_id=usuario_id
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@document_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_document_info(document_id):
    """
    Obtiene información de un documento específico
    """
    try:
        document_info = document_service.get_document_info(document_id)
        
        if document_info:
            return jsonify({
                'success': True,
                'document': document_info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Documento no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo información del documento: {str(e)}'
        }), 500

@document_bp.route('/<int:document_id>/download', methods=['GET'])
@login_required
def download_document(document_id):
    """
    Descarga un documento específico
    """
    try:
        documento = DocumentoContrato.get_by_id(document_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'error': 'Documento no encontrado'
            }), 404
        
        if not os.path.exists(documento.ruta_archivo):
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado en el servidor'
            }), 404
        
        return send_file(
            documento.ruta_archivo,
            as_attachment=True,
            download_name=documento.nombre_archivo
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error descargando documento: {str(e)}'
        }), 500

@document_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """
    Elimina un documento específico
    """
    try:
        delete_file = request.args.get('delete_file', 'true').lower() == 'true'
        
        result = document_service.delete_document(
            document_id=document_id,
            delete_file=delete_file
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error eliminando documento: {str(e)}'
        }), 500

@document_bp.route('/contract/<int:contrato_id>', methods=['GET'])
@login_required
def get_documents_by_contract(contrato_id):
    """
    Obtiene todos los documentos de un contrato específico
    """
    try:
        documents = document_service.get_documents_by_contract(contrato_id)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo documentos del contrato: {str(e)}'
        }), 500

@document_bp.route('/list', methods=['GET'])
@login_required
def list_all_documents():
    """
    Lista todos los documentos del sistema
    """
    try:
        # Parámetros de paginación opcionales
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        documents = document_service.get_all_documents()
        
        # Aplicar paginación simple
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_documents = documents[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'documents': paginated_documents,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': len(documents),
                'total_pages': (len(documents) + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error listando documentos: {str(e)}'
        }), 500

@document_bp.route('/stats', methods=['GET'])
@login_required
def get_storage_stats():
    """
    Obtiene estadísticas de almacenamiento de documentos
    """
    try:
        stats = document_service.get_storage_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo estadísticas: {str(e)}'
        }), 500

@document_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup_orphaned_files():
    """
    Limpia archivos huérfanos del sistema
    """
    try:
        result = document_service.cleanup_orphaned_files()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en limpieza de archivos: {str(e)}'
        }), 500

@document_bp.route('/validate', methods=['POST'])
@login_required
def validate_documents():
    """
    Valida la integridad de todos los documentos
    """
    try:
        documents = document_service.get_all_documents()
        
        validation_results = {
            'total_documents': len(documents),
            'valid_documents': 0,
            'missing_files': 0,
            'invalid_documents': [],
            'missing_file_details': []
        }
        
        for doc in documents:
            if doc['file_exists']:
                validation_results['valid_documents'] += 1
            else:
                validation_results['missing_files'] += 1
                validation_results['missing_file_details'].append({
                    'id': doc['id'],
                    'nombre_archivo': doc['nombre_archivo'],
                    'contrato_id': doc['contrato_id'],
                    'contrato_titulo': doc.get('contrato_titulo', 'N/A'),
                    'ruta_archivo': doc['ruta_archivo']
                })
        
        return jsonify({
            'success': True,
            'validation': validation_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error validando documentos: {str(e)}'
        }), 500