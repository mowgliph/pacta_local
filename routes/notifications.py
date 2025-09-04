from flask import Blueprint, jsonify, request, session, url_for
from functools import wraps
from datetime import datetime, timedelta
from database.models import Notificacion, Contrato

notifications_bp = Blueprint('notifications', __name__)

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

# ===== RUTAS API DE NOTIFICACIONES =====

@notifications_bp.route('/api/notifications')
@api_login_required
def get_notifications():
    """Obtiene las notificaciones del usuario actual"""
    try:
        user_id = session.get('user_id')
        notifications = Notificacion.get_by_user(user_id, limit=50)
        
        notifications_data = [notification.to_dict() for notification in notifications]
        
        return jsonify({
            'success': True,
            'notifications': notifications_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener notificaciones: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/count')
@api_login_required
def get_notification_count():
    """Obtiene el contador de notificaciones no leídas"""
    try:
        user_id = session.get('user_id')
        unread_notifications = Notificacion.get_by_user(user_id, unread_only=True)
        
        return jsonify({
            'success': True,
            'count': len(unread_notifications)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener contador: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@api_login_required
def mark_notification_read(notification_id):
    """Marca una notificación como leída"""
    try:
        Notificacion.mark_as_read(notification_id)
        
        return jsonify({
            'success': True,
            'message': 'Notificación marcada como leída'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al marcar notificación: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/mark-all-read', methods=['POST'])
@api_login_required
def mark_all_notifications_read():
    """Marca todas las notificaciones del usuario como leídas"""
    try:
        user_id = session.get('user_id')
        Notificacion.mark_all_as_read(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Todas las notificaciones marcadas como leídas'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al marcar notificaciones: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/create', methods=['POST'])
@api_login_required
def create_notification():
    """Crea una nueva notificación del sistema"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'system')
        
        if not title or not message:
            return jsonify({
                'success': False,
                'message': 'Título y mensaje son requeridos'
            }), 400
        
        notification = Notificacion.create_system_notification(
            usuario_id=user_id,
            title=title,
            message=message
        )
        
        return jsonify({
            'success': True,
            'message': 'Notificación creada exitosamente',
            'notification': notification.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear notificación: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/check-contracts', methods=['POST'])
@api_login_required
def check_contract_reminders():
    """Verifica contratos próximos a vencer y crea notificaciones"""
    try:
        user_id = session.get('user_id')
        
        # Obtener contratos próximos a vencer (30 días)
        today = datetime.now().date()
        warning_date = today + timedelta(days=30)
        
        contratos = Contrato.get_all()
        notifications_created = 0
        
        for contrato in contratos:
            if contrato.fecha_fin and contrato.fecha_fin <= warning_date and contrato.estado == 'activo':
                days_remaining = (contrato.fecha_fin - today).days
                
                if days_remaining <= 30 and days_remaining >= 0:
                    # Verificar si ya existe una notificación para este contrato
                    existing_notifications = Notificacion.get_by_user(user_id)
                    contract_notified = any(
                        n.contract_id == contrato.id and n.type == 'contract_expiring' and not n.is_read
                        for n in existing_notifications
                    )
                    
                    if not contract_notified:
                        title = f"Contrato próximo a vencer: {contrato.numero_contrato}"
                        message = f"El contrato '{contrato.titulo}' vence en {days_remaining} días ({contrato.fecha_fin})"
                        
                        notification = Notificacion(
                            usuario_id=user_id,
                            title=title,
                            message=message,
                            type='contract_expiring',
                            contract_id=contrato.id
                        )
                        notification.save()
                        notifications_created += 1
        
        return jsonify({
            'success': True,
            'message': f'Verificación completada. {notifications_created} notificaciones creadas.',
            'notifications_created': notifications_created
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al verificar contratos: {str(e)}'
        }), 500