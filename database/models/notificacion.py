from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Notificacion:
    def __init__(self, id=None, usuario_id=None, title=None, message=None, type='system', is_read=False, created_at=None, contract_id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.title = title
        self.message = message
        self.type = type  # 'system', 'contract_expiring', 'contract_expired', 'user', 'report'
        self.is_read = is_read
        self.created_at = created_at
        self.contract_id = contract_id  # Para notificaciones relacionadas con contratos
    
    def save(self):
        """Guarda o actualiza la notificación en la base de datos"""
        if self.id:
            # Actualizar notificación existente
            query = '''
                UPDATE notificaciones 
                SET usuario_id=?, title=?, message=?, type=?, is_read=?, contract_id=?
                WHERE id=?
            '''
            params = (self.usuario_id, self.title, self.message, self.type, self.is_read, self.contract_id, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nueva notificación
            query = '''
                INSERT INTO notificaciones (usuario_id, title, message, type, is_read, contract_id)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (self.usuario_id, self.title, self.message, self.type, self.is_read, self.contract_id)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_user(cls, usuario_id, limit=50, unread_only=False):
        """Obtiene notificaciones de un usuario específico"""
        query = "SELECT * FROM notificaciones WHERE usuario_id = ?"
        params = [usuario_id]
        
        if unread_only:
            query += " AND is_read = 0"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        results = db_manager.execute_query(query, params)
        notificaciones = []
        for row in results:
            notificaciones.append(cls(
                id=row['id'],
                usuario_id=row['usuario_id'],
                title=row['title'],
                message=row['message'],
                type=row['type'],
                is_read=bool(row['is_read']),
                created_at=row['created_at'],
                contract_id=row['contract_id']
            ))
        return notificaciones
    
    @classmethod
    def get_unread_count(cls, usuario_id):
        """Obtiene el número de notificaciones no leídas de un usuario"""
        query = "SELECT COUNT(*) as count FROM notificaciones WHERE usuario_id = ? AND is_read = 0"
        result = db_manager.execute_query(query, (usuario_id,))
        return result[0]['count'] if result else 0
    
    @classmethod
    def mark_as_read(cls, notification_id):
        """Marca una notificación como leída"""
        query = "UPDATE notificaciones SET is_read = 1 WHERE id = ?"
        db_manager.execute_update(query, (notification_id,))
    
    @classmethod
    def mark_all_as_read(cls, usuario_id):
        """Marca todas las notificaciones de un usuario como leídas"""
        query = "UPDATE notificaciones SET is_read = 1 WHERE usuario_id = ?"
        db_manager.execute_update(query, (usuario_id,))
    
    @classmethod
    def create_system_notification(cls, usuario_id, title, message):
        """Crea una notificación del sistema"""
        notification = cls(
            usuario_id=usuario_id,
            title=title,
            message=message,
            type='system'
        )
        return notification.save()
    
    @classmethod
    def create_contract_expiring_notification(cls, usuario_id, contract_id, contract_number, days_until_expiry):
        """Crea una notificación de contrato próximo a vencer"""
        title = "Contrato próximo a vencer"
        message = f"El contrato {contract_number} vencerá en {days_until_expiry} días"
        
        notification = cls(
            usuario_id=usuario_id,
            title=title,
            message=message,
            type='contract_expiring',
            contract_id=contract_id
        )
        return notification.save()
    
    @classmethod
    def create_contract_expired_notification(cls, usuario_id, contract_id, contract_number):
        """Crea una notificación de contrato vencido"""
        title = "Contrato vencido"
        message = f"El contrato {contract_number} ha vencido"
        
        notification = cls(
            usuario_id=usuario_id,
            title=title,
            message=message,
            type='contract_expired',
            contract_id=contract_id
        )
        return notification.save()
    
    @classmethod
    def delete_old_notifications(cls, days=30):
        """Elimina notificaciones antiguas (por defecto más de 30 días)"""
        query = "DELETE FROM notificaciones WHERE created_at < datetime('now', '-{} days')".format(days)
        db_manager.execute_update(query)
    
    def to_dict(self):
        """Convierte la notificación a diccionario para JSON"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at,
            'contract_id': self.contract_id
        }