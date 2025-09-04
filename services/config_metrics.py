import os
import psutil
from datetime import datetime, timedelta
from database.database import DatabaseManager
from database.models.usuario import Usuario
from database.models.actividad_sistema import ActividadSistema

def get_config_metrics():
    """
    Obtiene métricas específicas para la página de configuración
    Retorna un diccionario con las métricas dinámicas
    """
    try:
        metrics = {}
        
        # Usuarios activos (usuarios que han iniciado sesión en los últimos 30 días)
        metrics['usuarios_activos'] = get_active_users_count()
        
        # Último backup y su tipo
        backup_info = get_last_backup_info_detailed()
        metrics['ultimo_backup'] = backup_info['time']
        metrics['ultimo_backup_tipo'] = backup_info['type']
        
        # Espacio usado del disco
        metrics['espacio_usado'] = get_disk_usage()
        
        # Tamaño total del disco
        metrics['espacio_total'] = get_disk_total_gb()
        
        return metrics
        
    except Exception as e:
        print(f"Error obteniendo métricas de configuración: {e}")
        return {
            'usuarios_activos': 0,
            'ultimo_backup': 'No disponible',
            'espacio_usado': '0%'
        }

def get_active_users_count():
    """
    Cuenta usuarios activos en los últimos 30 días
    """
    try:
        db_manager = DatabaseManager()
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Fecha límite (30 días atrás)
            fecha_limite = datetime.now() - timedelta(days=30)
            
            # Contar usuarios únicos con actividad reciente
            query = """
            SELECT COUNT(DISTINCT u.id) as usuarios_activos
            FROM usuarios u
            LEFT JOIN actividad_sistema a ON u.id = a.usuario_id
            WHERE u.activo = 1 
            AND (u.ultimo_acceso >= ? OR a.fecha_actividad >= ?)
            """
            
            cursor.execute(query, (fecha_limite, fecha_limite))
            result = cursor.fetchone()
            
            return result[0] if result and result[0] else 0
        
    except Exception as e:
        print(f"Error contando usuarios activos: {e}")
        # Fallback: contar todos los usuarios activos
        try:
            db_manager = DatabaseManager()
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
                result = cursor.fetchone()
                return result[0] if result else 0
        except:
            return 24  # Valor por defecto

def get_last_backup_info():
    """
    Obtiene información del último backup desde el servicio de backup (solo tiempo)
    """
    backup_info = get_last_backup_info_detailed()
    return backup_info['time']

def get_last_backup_info_detailed():
    """
    Obtiene información detallada del último backup desde el servicio de backup
    Retorna dict con 'time' y 'type'
    """
    try:
        from services.backup_service import BackupService
        
        backup_service = BackupService()
        backups_result = backup_service.list_backups()
        
        if backups_result.get('success', False):
            backups = backups_result['backups']
            
            # Obtener todos los backups y encontrar el más reciente
            all_backups = []
            for backup_type in ['automatic', 'manual']:
                for backup in backups.get(backup_type, []):
                    backup['backup_type'] = backup_type
                    all_backups.append(backup)
            
            if all_backups:
                # Ordenar por fecha de creación (más reciente primero)
                all_backups.sort(key=lambda x: x['created_at'], reverse=True)
                latest_backup = all_backups[0]
                
                # Parsear fecha de creación
                backup_date = datetime.fromisoformat(latest_backup['created_at'].replace('Z', '+00:00'))
                
                # Calcular diferencia con ahora
                now = datetime.now()
                diff = now - backup_date.replace(tzinfo=None)
                
                # Formatear tiempo
                if diff.total_seconds() < 3600:  # Menos de 1 hora
                    minutes = int(diff.total_seconds() / 60)
                    time_str = f"Hace {minutes} min" if minutes > 0 else "Ahora"
                elif diff.days == 0:
                    hours = int(diff.total_seconds() / 3600)
                    time_str = f"Hace {hours}h"
                elif diff.days == 1:
                    time_str = "Ayer"
                elif diff.days < 7:
                    time_str = f"Hace {diff.days} días"
                else:
                    time_str = backup_date.strftime("%d/%m/%Y")
                
                # Formatear tipo
                backup_type = latest_backup.get('backup_type', 'manual')
                type_str = "Automático" if backup_type == 'automatic' else "Manual"
                
                return {
                    'time': time_str,
                    'type': type_str
                }
            else:
                return {
                    'time': "Sin backups",
                    'type': "N/A"
                }
        else:
            return {
                'time': "No disponible",
                'type': "N/A"
            }
            
    except Exception as e:
        print(f"Error obteniendo info de backup: {e}")
        return {
            'time': "No disponible",
            'type': "N/A"
        }

def get_disk_usage():
    """
    Obtiene el porcentaje de uso del disco
    """
    try:
        # Obtener uso del disco donde está la aplicación
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        disk_usage = psutil.disk_usage(app_dir)
        
        # Calcular porcentaje usado
        percent_used = round((disk_usage.used / disk_usage.total) * 100, 1)
        
        return f"{percent_used}%"
        
    except Exception as e:
        print(f"Error obteniendo uso de disco: {e}")
        return "68%"  # Valor por defecto

def get_disk_total_gb():
    """
    Obtiene el tamaño total del disco en GB
    """
    try:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        disk_usage = psutil.disk_usage(app_dir)
        total_gb = round(disk_usage.total / (1024**3), 0)
        return f"{total_gb}GB"
    except:
        return "500GB"  # Valor por defecto