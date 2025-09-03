#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Recordatorios de Contratos
Genera notificaciones automáticas para contratos próximos a vencer
"""

from datetime import datetime, timedelta
from database import db_manager
from database.models import Contrato, Notificacion, Usuario
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractReminderSystem:
    """Sistema de recordatorios para contratos"""
    
    def __init__(self):
        self.reminder_periods = {
            'urgent': 7,      # 7 días antes
            'warning': 30,    # 30 días antes
            'notice': 90      # 90 días antes
        }
    
    def check_expiring_contracts(self):
        """Verifica contratos próximos a vencer y genera notificaciones"""
        try:
            logger.info("Iniciando verificación de contratos próximos a vencer")
            
            # Obtener todos los contratos activos
            contratos = Contrato.get_all()
            active_contracts = [c for c in contratos if c.estado == 'activo']
            
            notifications_created = 0
            
            for contrato in active_contracts:
                notifications_created += self._process_contract_reminders(contrato)
            
            logger.info(f"Proceso completado. {notifications_created} notificaciones creadas")
            return notifications_created
            
        except Exception as e:
            logger.error(f"Error al verificar contratos: {str(e)}")
            return 0
    
    def _process_contract_reminders(self, contrato):
        """Procesa recordatorios para un contrato específico"""
        notifications_created = 0
        
        try:
            # Calcular días hasta vencimiento
            today = datetime.now().date()
            expiry_date = contrato.fecha_fin.date() if hasattr(contrato.fecha_fin, 'date') else contrato.fecha_fin
            days_until_expiry = (expiry_date - today).days
            
            # Verificar si el contrato ya venció
            if days_until_expiry < 0:
                notifications_created += self._create_expired_notification(contrato)
                return notifications_created
            
            # Verificar cada período de recordatorio
            for reminder_type, days_before in self.reminder_periods.items():
                if days_until_expiry <= days_before:
                    # Verificar si ya existe una notificación reciente para este contrato y tipo
                    if not self._notification_exists_recently(contrato.id, reminder_type):
                        notifications_created += self._create_reminder_notification(
                            contrato, reminder_type, days_until_expiry
                        )
            
            return notifications_created
            
        except Exception as e:
            logger.error(f"Error procesando contrato {contrato.numero_contrato}: {str(e)}")
            return 0
    
    def _create_reminder_notification(self, contrato, reminder_type, days_until_expiry):
        """Crea notificación de recordatorio"""
        try:
            # Definir títulos y mensajes según el tipo de recordatorio
            titles = {
                'urgent': '🚨 Contrato Próximo a Vencer',
                'warning': '⚠️ Contrato Vence Pronto',
                'notice': '📅 Recordatorio de Vencimiento'
            }
            
            messages = {
                'urgent': f'El contrato {contrato.numero_contrato} vence en {days_until_expiry} días. Acción inmediata requerida.',
                'warning': f'El contrato {contrato.numero_contrato} vence en {days_until_expiry} días. Considere renovar o tomar acción.',
                'notice': f'El contrato {contrato.numero_contrato} vence en {days_until_expiry} días. Planifique la renovación.'
            }
            
            title = titles.get(reminder_type, 'Recordatorio de Contrato')
            message = messages.get(reminder_type, f'Contrato {contrato.numero_contrato} requiere atención.')
            
            # Crear notificación para el usuario responsable
            Notificacion.create_contract_notification(
                user_id=contrato.usuario_responsable_id,
                title=title,
                message=message,
                contract_id=contrato.id
            )
            
            logger.info(f"Notificación {reminder_type} creada para contrato {contrato.numero_contrato}")
            return 1
            
        except Exception as e:
            logger.error(f"Error creando notificación para contrato {contrato.numero_contrato}: {str(e)}")
            return 0
    
    def _create_expired_notification(self, contrato):
        """Crea notificación para contrato vencido"""
        try:
            # Verificar si ya existe notificación de vencimiento reciente
            if self._notification_exists_recently(contrato.id, 'expired'):
                return 0
            
            today = datetime.now().date()
            expiry_date = contrato.fecha_fin.date() if hasattr(contrato.fecha_fin, 'date') else contrato.fecha_fin
            days_expired = (today - expiry_date).days
            
            title = '🔴 Contrato Vencido'
            message = f'El contrato {contrato.numero_contrato} venció hace {days_expired} días. Requiere atención inmediata.'
            
            Notificacion.create_contract_notification(
                user_id=contrato.usuario_responsable_id,
                title=title,
                message=message,
                contract_id=contrato.id
            )
            
            logger.info(f"Notificación de vencimiento creada para contrato {contrato.numero_contrato}")
            return 1
            
        except Exception as e:
            logger.error(f"Error creando notificación de vencimiento para contrato {contrato.numero_contrato}: {str(e)}")
            return 0
    
    def _notification_exists_recently(self, contract_id, notification_type, days=1):
        """Verifica si ya existe una notificación reciente para el contrato"""
        try:
            # Buscar notificaciones recientes para este contrato
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT COUNT(*) as count
                FROM notificaciones 
                WHERE contract_id = ? 
                AND created_at >= ? 
                AND (title LIKE ? OR message LIKE ?)
            """
            
            # Patrones de búsqueda según el tipo
            patterns = {
                'urgent': '%Próximo a Vencer%',
                'warning': '%Vence Pronto%',
                'notice': '%Recordatorio%',
                'expired': '%Vencido%'
            }
            
            pattern = patterns.get(notification_type, '%')
            
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (contract_id, cutoff_date, pattern, pattern))
                result = cursor.fetchone()
                return result['count'] > 0 if result else False
                
        except Exception as e:
            logger.error(f"Error verificando notificaciones existentes: {str(e)}")
            return False
    
    def create_system_reminders(self):
        """Crea recordatorios del sistema para administradores"""
        try:
            # Obtener estadísticas de contratos
            contratos = Contrato.get_all()
            active_contracts = [c for c in contratos if c.estado == 'activo']
            
            today = datetime.now().date()
            expiring_soon = []
            expired = []
            
            for contrato in active_contracts:
                expiry_date = contrato.fecha_fin.date() if hasattr(contrato.fecha_fin, 'date') else contrato.fecha_fin
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry < 0:
                    expired.append(contrato)
                elif days_until_expiry <= 30:
                    expiring_soon.append(contrato)
            
            # Crear notificación para administradores si hay contratos que requieren atención
            if expiring_soon or expired:
                admins = [u for u in Usuario.get_all() if u.es_admin]
                
                title = '📊 Resumen de Contratos - Atención Requerida'
                message = f'Contratos que requieren atención: {len(expiring_soon)} próximos a vencer, {len(expired)} vencidos.'
                
                notifications_created = 0
                for admin in admins:
                    Notificacion.create_system_notification(
                        user_id=admin.id,
                        title=title,
                        message=message
                    )
                    notifications_created += 1
                
                logger.info(f"Notificaciones de resumen enviadas a {notifications_created} administradores")
                return notifications_created
            
            return 0
            
        except Exception as e:
            logger.error(f"Error creando recordatorios del sistema: {str(e)}")
            return 0

def run_contract_reminders():
    """Función principal para ejecutar el sistema de recordatorios"""
    reminder_system = ContractReminderSystem()
    
    # Verificar contratos individuales
    individual_notifications = reminder_system.check_expiring_contracts()
    
    # Crear recordatorios del sistema
    system_notifications = reminder_system.create_system_reminders()
    
    total_notifications = individual_notifications + system_notifications
    
    print(f"Sistema de recordatorios ejecutado exitosamente.")
    print(f"Total de notificaciones creadas: {total_notifications}")
    print(f"- Notificaciones individuales: {individual_notifications}")
    print(f"- Notificaciones del sistema: {system_notifications}")
    
    return total_notifications

if __name__ == '__main__':
    run_contract_reminders()