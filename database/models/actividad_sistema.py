from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class ActividadSistema:
    def __init__(self, id=None, usuario_id=None, accion=None, tabla_afectada=None, registro_id=None, detalles=None, fecha_actividad=None):
        self.id = id
        self.usuario_id = usuario_id
        self.accion = accion
        self.tabla_afectada = tabla_afectada
        self.registro_id = registro_id
        self.detalles = detalles
        self.fecha_actividad = fecha_actividad
    
    def save(self):
        """Guarda la actividad en la base de datos"""
        query = '''
            INSERT INTO actividad_sistema (usuario_id, accion, tabla_afectada, registro_id, detalles)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (self.usuario_id, self.accion, self.tabla_afectada, self.registro_id, self.detalles)
        self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_recent(cls, limit=50):
        """Obtiene las actividades más recientes"""
        query = "SELECT * FROM actividad_sistema ORDER BY fecha_actividad DESC LIMIT ?"
        results = db_manager.execute_query(query, (limit,))
        actividades = []
        for row in results:
            actividades.append(cls(
                id=row['id'],
                usuario_id=row['usuario_id'],
                accion=row['accion'],
                tabla_afectada=row['tabla_afectada'],
                registro_id=row['registro_id'],
                detalles=row['detalles'],
                fecha_actividad=row['fecha_actividad']
            ))
        return actividades