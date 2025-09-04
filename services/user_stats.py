from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

def get_user_personal_stats(user_id):
    """
    Obtiene las estadísticas personales de un usuario específico
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        dict: Diccionario con las estadísticas personales del usuario
    """
    try:
        stats = {
            'contratos_creados': 0,
            'reportes_generados': 0,
            'ultimo_acceso': 'No disponible',
            'sesiones_mes': 0
        }
        
        # Obtener contratos creados por el usuario
        query_contratos = """
            SELECT COUNT(*) as total 
            FROM contratos 
            WHERE usuario_responsable_id = ?
        """
        result = db_manager.execute_query(query_contratos, (user_id,))
        if result:
            stats['contratos_creados'] = result[0][0]
        
        # Obtener reportes generados (basado en actividad del sistema)
        query_reportes = """
            SELECT COUNT(*) as total 
            FROM actividad_sistema 
            WHERE usuario_id = ? AND accion LIKE '%reporte%'
        """
        result = db_manager.execute_query(query_reportes, (user_id,))
        if result:
            stats['reportes_generados'] = result[0][0]
        
        # Obtener último acceso (basado en la actividad más reciente)
        query_ultimo_acceso = """
            SELECT fecha_actividad 
            FROM actividad_sistema 
            WHERE usuario_id = ? 
            ORDER BY fecha_actividad DESC 
            LIMIT 1
        """
        result = db_manager.execute_query(query_ultimo_acceso, (user_id,))
        if result and result[0][0]:
            fecha_str = result[0][0]
            try:
                # Intentar parsear la fecha
                if isinstance(fecha_str, str):
                    fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                else:
                    fecha = fecha_str
                
                # Formatear la fecha de manera amigable
                ahora = datetime.now()
                diferencia = ahora - fecha.replace(tzinfo=None)
                
                if diferencia.days == 0:
                    if diferencia.seconds < 3600:  # Menos de 1 hora
                        minutos = diferencia.seconds // 60
                        stats['ultimo_acceso'] = f'Hace {minutos} minutos'
                    else:  # Menos de 24 horas
                        horas = diferencia.seconds // 3600
                        stats['ultimo_acceso'] = f'Hace {horas} horas'
                elif diferencia.days == 1:
                    stats['ultimo_acceso'] = 'Ayer'
                elif diferencia.days < 7:
                    stats['ultimo_acceso'] = f'Hace {diferencia.days} días'
                else:
                    stats['ultimo_acceso'] = fecha.strftime('%d/%m/%Y')
            except Exception as e:
                print(f"Error al procesar fecha: {e}")
                stats['ultimo_acceso'] = 'Hoy'
        
        # Obtener sesiones del mes actual (basado en actividades del mes)
        primer_dia_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query_sesiones_mes = """
            SELECT COUNT(DISTINCT DATE(fecha_actividad)) as dias_activos
            FROM actividad_sistema 
            WHERE usuario_id = ? AND fecha_actividad >= ?
        """
        result = db_manager.execute_query(query_sesiones_mes, (user_id, primer_dia_mes.isoformat()))
        if result:
            stats['sesiones_mes'] = result[0][0]
        
        return stats
        
    except Exception as e:
        print(f"Error al obtener estadísticas personales: {e}")
        # Retornar valores por defecto en caso de error
        return {
            'contratos_creados': 0,
            'reportes_generados': 0,
            'ultimo_acceso': 'No disponible',
            'sesiones_mes': 0
        }

def get_user_activity_summary(user_id, days=30):
    """
    Obtiene un resumen de la actividad del usuario en los últimos días
    
    Args:
        user_id (int): ID del usuario
        days (int): Número de días hacia atrás para el análisis
        
    Returns:
        dict: Resumen de actividad del usuario
    """
    try:
        fecha_limite = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                accion,
                COUNT(*) as cantidad,
                MAX(fecha_actividad) as ultima_vez
            FROM actividad_sistema 
            WHERE usuario_id = ? AND fecha_actividad >= ?
            GROUP BY accion
            ORDER BY cantidad DESC
        """
        
        result = db_manager.execute_query(query, (user_id, fecha_limite.isoformat()))
        
        actividades = []
        if result:
            for row in result:
                actividades.append({
                    'accion': row[0],
                    'cantidad': row[1],
                    'ultima_vez': row[2]
                })
        
        return {
            'periodo_dias': days,
            'actividades': actividades,
            'total_acciones': sum(act['cantidad'] for act in actividades)
        }
        
    except Exception as e:
        print(f"Error al obtener resumen de actividad: {e}")
        return {
            'periodo_dias': days,
            'actividades': [],
            'total_acciones': 0
        }