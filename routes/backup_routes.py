from flask import Blueprint, request, jsonify, send_file, session, url_for
from functools import wraps
from datetime import datetime
from pathlib import Path
from services.backup_service import BackupService
from services.restore_service import RestoreService
from services.change_detection_service import ChangeDetectionService
from services.backup_scheduler import get_backup_scheduler
import os
import zipfile

# Decorador para rutas API que requieren login
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'message': 'No autenticado',
                'redirect': url_for('auth.login')
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Crear blueprint para las rutas de backup
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

# Inicializar servicios
backup_service = BackupService()
restore_service = RestoreService()
change_detection_service = ChangeDetectionService()

@backup_bp.route('/create', methods=['POST'])
@api_login_required
def create_backup():
    """
    Crea un backup manual
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Backup manual solicitado por usuario')
        backup_name = data.get('name', None)
        description = data.get('description', '')
        
        # Si se proporciona descripción, agregarla a la razón
        if description:
            reason = f"{reason} - {description}"
        
        # Crear backup manual
        result = backup_service.create_backup(
            backup_type='manual',
            reason=reason,
            custom_name=backup_name
        )
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result['message'],
                'backup_info': result['backup_info']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error desconocido'),
                'message': result.get('message', 'Error creando backup')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error interno: {str(e)}'
        }), 500

@backup_bp.route('/list', methods=['GET'])
@api_login_required
def list_backups():
    """
    Lista todos los backups disponibles
    """
    try:
        result = backup_service.list_backups()
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'backups': result['backups']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error listando backups')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/delete', methods=['POST'])
@api_login_required
def delete_backup_endpoint():
    """
    Elimina un backup específico
    """
    try:
        data = request.get_json() or {}
        backup_type = data.get('type')
        backup_name = data.get('name')
        
        if not backup_type or not backup_name:
            return jsonify({
                'success': False,
                'error': 'Parámetros type y name son requeridos'
            }), 400
        
        if backup_type not in ['automatic', 'manual', 'imported']:
            return jsonify({
                'success': False,
                'error': 'Tipo de backup inválido'
            }), 400
        
        # Construir ruta del backup
        backup_path = Path('backups') / backup_type / f"{backup_name}.zip"
        
        if not backup_path.exists():
            return jsonify({
                'success': False,
                'error': 'Archivo de backup no encontrado'
            }), 404
        
        # Usar el servicio para eliminar el backup
        result = backup_service.delete_backup(str(backup_path))
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': f'Backup {backup_name} eliminado exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error eliminando backup')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/config', methods=['GET'])
@api_login_required
def get_backup_config():
    """
    Obtiene la configuración actual de backups automáticos
    """
    try:
        scheduler = get_backup_scheduler()
        
        # Obtener configuración actual del job de backup diario
        daily_job = scheduler.scheduler.get_job('daily_backup')
        
        config = {
            'enabled': daily_job is not None,
            'time': '16:00',  # Valor por defecto
            'name_pattern': 'Auto_Backup_{date}',
            'retention_days': 7
        }
        
        if daily_job and daily_job.trigger:
            # Extraer hora del trigger de forma más segura
            trigger = daily_job.trigger
            try:
                if hasattr(trigger, 'fields') and len(trigger.fields) > 2:
                    # Los campos en CronTrigger son: [second, minute, hour, day, month, day_of_week, year]
                    hour_field = trigger.fields[2]  # hour field
                    minute_field = trigger.fields[1]  # minute field
                    
                    # Extraer valores de los campos
                    hour = 16  # valor por defecto
                    minute = 0  # valor por defecto
                    
                    if hasattr(hour_field, 'expressions') and hour_field.expressions:
                        hour = hour_field.expressions[0].step if hasattr(hour_field.expressions[0], 'step') else hour_field.expressions[0]
                    
                    if hasattr(minute_field, 'expressions') and minute_field.expressions:
                        minute = minute_field.expressions[0].step if hasattr(minute_field.expressions[0], 'step') else minute_field.expressions[0]
                    
                    config['time'] = f"{hour:02d}:{minute:02d}"
            except (AttributeError, IndexError, TypeError):
                # Si hay algún error extrayendo la hora, usar valor por defecto
                config['time'] = '16:00'
        
        return jsonify({
            'success': True,
            'config': config
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/config', methods=['POST'])
@api_login_required
def save_backup_config():
    """
    Guarda la configuración de backups automáticos
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos requeridos'
            }), 400
        
        enabled = data.get('enabled', True)
        time_str = data.get('time', '16:00')
        name_pattern = data.get('name_pattern', 'Auto_Backup_{date}')
        retention_days = data.get('retention_days', 7)
        
        # Validar formato de hora
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Hora inválida")
        except (ValueError, IndexError):
            return jsonify({
                'success': False,
                'error': 'Formato de hora inválido. Use HH:MM'
            }), 400
        
        # Validar días de retención
        try:
            retention_days = int(retention_days)
            if retention_days < 1:
                raise ValueError("Días de retención debe ser mayor a 0")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Días de retención debe ser un número válido mayor a 0'
            }), 400
        
        scheduler = get_backup_scheduler()
        
        if enabled:
            # Reprogramar el backup automático
            result = scheduler.reschedule_daily_backup(hour, minute)
            if not result.get('success', False):
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Error reprogramando backup')
                }), 500
        else:
            # Desactivar el backup automático
            try:
                scheduler.scheduler.remove_job('daily_backup')
            except:
                pass  # Job ya no existe
        
        return jsonify({
            'success': True,
            'message': 'Configuración guardada exitosamente',
            'config': {
                'enabled': enabled,
                'time': time_str,
                'name_pattern': name_pattern,
                'retention_days': retention_days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/download/<backup_type>/<backup_name>', methods=['GET'])
@api_login_required
def download_backup(backup_type, backup_name):
    """
    Descarga un archivo de backup
    
    Args:
        backup_type: 'automatic' o 'manual'
        backup_name: Nombre del archivo de backup (sin extensión)
    """
    try:
        if backup_type not in ['automatic', 'manual']:
            return jsonify({
                'success': False,
                'error': 'Tipo de backup inválido'
            }), 400
        
        backup_path = Path('backups') / backup_type / f"{backup_name}.zip"
        
        if not backup_path.exists():
            return jsonify({
                'success': False,
                'error': 'Archivo de backup no encontrado'
            }), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=f"{backup_name}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/download', methods=['GET'])
@api_login_required
def download_backup_query():
    """
    Descarga un archivo de backup usando parámetros de consulta
    
    Query params:
        type: 'automatic' o 'manual'
        name: Nombre del archivo de backup (sin extensión)
    """
    try:
        backup_type = request.args.get('type')
        backup_name = request.args.get('name')
        
        if not backup_type or not backup_name:
            return jsonify({
                'success': False,
                'error': 'Parámetros type y name son requeridos'
            }), 400
        
        if backup_type not in ['automatic', 'manual']:
            return jsonify({
                'success': False,
                'error': 'Tipo de backup inválido'
            }), 400
        
        backup_path = Path('backups') / backup_type / f"{backup_name}.zip"
        
        if not backup_path.exists():
            return jsonify({
                'success': False,
                'error': 'Archivo de backup no encontrado'
            }), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=f"{backup_name}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/upload', methods=['POST'])
@api_login_required
def upload_backup():
    """
    Sube un archivo de backup al sistema
    """
    try:
        # Verificar que se envió un archivo
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo de backup'
            }), 400
        
        file = request.files['backup_file']
        
        # Verificar que el archivo no esté vacío
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            }), 400
        
        # Verificar que sea un archivo .zip
        if not file.filename.lower().endswith('.zip'):
            return jsonify({
                'success': False,
                'error': 'Solo se permiten archivos .zip'
            }), 400
        
        # Crear directorio de backups importados si no existe
        import_dir = Path('backups') / 'imported'
        import_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = Path(file.filename).stem
        backup_filename = f"imported_{original_name}_{timestamp}.zip"
        backup_path = import_dir / backup_filename
        
        # Guardar archivo
        file.save(str(backup_path))
        
        # Verificar que el archivo se guardó correctamente
        if not backup_path.exists():
            return jsonify({
                'success': False,
                'error': 'Error al guardar el archivo'
            }), 500
        
        # Validar que el archivo es un backup válido
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Verificar que contiene los archivos esperados de un backup
                files_in_zip = zipf.namelist()
                # Buscar archivos de base de datos (database.db o pacta_local.db)
                has_db = any(f.endswith('.db') and ('database.db' in f or 'pacta_local.db' in f) for f in files_in_zip)
                
                if not has_db:
                    # El archivo no es válido, se eliminará después de cerrar el ZIP
                    is_valid = False
                else:
                    is_valid = True
            
            # Eliminar archivo inválido después de cerrar el ZIP
            if not is_valid:
                backup_path.unlink()
                return jsonify({
                    'success': False,
                    'error': 'El archivo no parece ser un backup válido de PACTA'
                }), 400
        
        except zipfile.BadZipFile:
            # Eliminar archivo corrupto después de cerrar cualquier referencia
            try:
                backup_path.unlink()
            except PermissionError:
                # Si no se puede eliminar, al menos reportar el error
                pass
            return jsonify({
                'success': False,
                'error': 'El archivo está corrupto o no es un archivo ZIP válido'
            }), 400
        
        # Obtener tamaño del archivo
        file_size_mb = round(backup_path.stat().st_size / (1024 * 1024), 2)
        
        return jsonify({
            'success': True,
            'message': 'Backup importado exitosamente',
            'backup_info': {
                'name': backup_filename.replace('.zip', ''),
                'type': 'imported',
                'size_mb': file_size_mb,
                'created_at': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error en upload_backup: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Error al importar backup: {str(e)}'
        }), 500

@backup_bp.route('/delete', methods=['DELETE'])
@api_login_required
def delete_backup():
    """
    Elimina un backup específico
    """
    try:
        data = request.get_json()
        
        if not data or 'backup_path' not in data:
            return jsonify({
                'success': False,
                'error': 'Ruta del backup requerida'
            }), 400
        
        backup_path = data['backup_path']
        
        # Verificar que el backup existe y es un archivo .zip
        backup_file = Path(backup_path)
        
        if not backup_file.exists() or backup_file.suffix != '.zip':
            return jsonify({
                'success': False,
                'error': 'Archivo de backup no válido'
            }), 400
        
        # No permitir eliminar backups fuera del directorio de backups
        if not str(backup_file.resolve()).startswith(str(Path('backups').resolve())):
            return jsonify({
                'success': False,
                'error': 'Ruta de backup no válida'
            }), 400
        
        result = backup_service.delete_backup(backup_path)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error eliminando backup')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/restore', methods=['POST'])
@api_login_required
def restore_backup():
    """
    Restaura la aplicación desde un backup
    """
    try:
        data = request.get_json()
        if not data or 'backup_path' not in data:
            return jsonify({
                'success': False,
                'error': 'Ruta del backup requerida'
            }), 400
        
        backup_path = data['backup_path']
        restore_options = data.get('restore_options', {})
        
        # Verificar que el backup existe
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return jsonify({
                'success': False,
                'error': 'Archivo de backup no encontrado'
            }), 404
        
        # Verificar que es un archivo de backup válido
        if not str(backup_file.resolve()).startswith(str(Path('backups').resolve())):
            return jsonify({
                'success': False,
                'error': 'Ruta de backup no válida'
            }), 400
        
        # Realizar la restauración
        result = restore_service.restore_from_backup(backup_path, restore_options)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result['message'],
                'backup_name': result.get('backup_name'),
                'restore_timestamp': result.get('restore_timestamp'),
                'current_backup_info': result.get('current_backup_info')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error en la restauración'),
                'message': result.get('message', 'Error restaurando backup')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error interno: {str(e)}'
        }), 500

@backup_bp.route('/validate', methods=['POST'])
@api_login_required
def validate_backup():
    """
    Valida la integridad de un archivo de backup
    """
    try:
        data = request.get_json()
        if not data or 'backup_path' not in data:
            return jsonify({
                'success': False,
                'error': 'Ruta del backup requerida'
            }), 400
        
        backup_path = data['backup_path']
        
        result = restore_service.validate_backup(backup_path)
        
        return jsonify(result), 200 if result.get('valid', False) else 400
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500

@backup_bp.route('/status', methods=['GET'])
@api_login_required
def backup_status():
    """
    Obtiene el estado del sistema de backup
    """
    try:
        # Obtener información del scheduler
        scheduler = get_backup_scheduler()
        scheduler_status = scheduler.get_job_status()
        
        # Obtener cambios pendientes
        changes_info = change_detection_service.has_changes_since_last_backup()
        
        # Obtener último backup
        last_backup_info = change_detection_service.get_last_backup_info()
        
        # Obtener estadísticas de backups
        backups_result = backup_service.list_backups()
        backup_stats = {
            'automatic_count': 0,
            'manual_count': 0,
            'total_size_mb': 0
        }
        
        if backups_result.get('success', False):
            backups = backups_result['backups']
            backup_stats['automatic_count'] = len(backups.get('automatic', []))
            backup_stats['manual_count'] = len(backups.get('manual', []))
            
            # Calcular tamaño total
            for backup_type in ['automatic', 'manual']:
                for backup in backups.get(backup_type, []):
                    backup_stats['total_size_mb'] += backup.get('size_mb', 0)
        
        return jsonify({
            'success': True,
            'scheduler_status': scheduler_status,
            'pending_changes': changes_info,
            'last_backup': last_backup_info,
            'backup_stats': backup_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/changes', methods=['GET'])
@api_login_required
def get_changes_summary():
    """
    Obtiene un resumen de cambios recientes
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        result = change_detection_service.get_change_summary(days)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'summary': result['summary'],
                'total_changes': result['total_changes'],
                'period_days': result['period_days']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error obteniendo resumen de cambios')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/cleanup', methods=['POST'])
@api_login_required
def cleanup_old_backups():
    """
    Ejecuta limpieza manual de backups obsoletos
    """
    try:
        result = backup_service.cleanup_old_backups()
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result['message'],
                'deleted_count': result.get('deleted_count', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error en limpieza')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/scheduler/trigger', methods=['POST'])
@api_login_required
def trigger_scheduled_backup():
    """
    Ejecuta manualmente el trabajo de backup programado
    """
    try:
        scheduler = get_backup_scheduler()
        result = scheduler.trigger_manual_backup()
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result.get('message', 'Backup ejecutado exitosamente'),
                'backup_info': result.get('backup_info')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error ejecutando backup'),
                'message': result.get('message', 'Error en backup programado')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/scheduler/reschedule', methods=['POST'])
@api_login_required
def reschedule_backup():
    """
    Reprograma la hora del backup automático
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos requeridos'
            }), 400
        
        hour = data.get('hour', 16)
        minute = data.get('minute', 0)
        
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            return jsonify({
                'success': False,
                'error': 'Hora o minuto inválidos'
            }), 400
        
        scheduler = get_backup_scheduler()
        result = scheduler.reschedule_daily_backup(hour, minute)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error reprogramando backup')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@backup_bp.route('/restore/history', methods=['GET'])
@api_login_required
def get_restore_history():
    """
    Obtiene el historial de restauraciones
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        result = restore_service.get_restore_history(limit)
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'history': result['history']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error obteniendo historial')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500