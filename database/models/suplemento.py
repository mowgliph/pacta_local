from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Suplemento:
    def __init__(self, id=None, contrato_id=None, numero_suplemento=None, tipo_modificacion=None, descripcion=None, monto_modificacion=0, fecha_modificacion=None, usuario_autoriza_id=None, estado='pendiente', fecha_creacion=None):
        self.id = id
        self.contrato_id = contrato_id
        self.numero_suplemento = numero_suplemento
        self.tipo_modificacion = tipo_modificacion
        self.descripcion = descripcion
        self.monto_modificacion = monto_modificacion
        self.fecha_modificacion = fecha_modificacion
        self.usuario_autoriza_id = usuario_autoriza_id
        self.estado = estado
        self.fecha_creacion = fecha_creacion
    
    def save(self):
        """Guarda o actualiza el suplemento en la base de datos"""
        if self.id:
            # Actualizar suplemento existente
            query = '''
                UPDATE suplementos 
                SET contrato_id=?, numero_suplemento=?, tipo_modificacion=?, descripcion=?, 
                    monto_modificacion=?, fecha_modificacion=?, usuario_autoriza_id=?, estado=?
                WHERE id=?
            '''
            params = (self.contrato_id, self.numero_suplemento, self.tipo_modificacion, self.descripcion, 
                     self.monto_modificacion, self.fecha_modificacion, self.usuario_autoriza_id, self.estado, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo suplemento
            query = '''
                INSERT INTO suplementos (contrato_id, numero_suplemento, tipo_modificacion, descripcion, 
                                       monto_modificacion, fecha_modificacion, usuario_autoriza_id, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.contrato_id, self.numero_suplemento, self.tipo_modificacion, self.descripcion, 
                     self.monto_modificacion, self.fecha_modificacion, self.usuario_autoriza_id, self.estado)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_contrato(cls, contrato_id):
        """Obtiene todos los suplementos de un contrato"""
        query = "SELECT * FROM suplementos WHERE contrato_id = ? ORDER BY fecha_creacion DESC"
        results = db_manager.execute_query(query, (contrato_id,))
        suplementos = []
        for row in results:
            suplementos.append(cls(
                id=row['id'],
                contrato_id=row['contrato_id'],
                numero_suplemento=row['numero_suplemento'],
                tipo_modificacion=row['tipo_modificacion'],
                descripcion=row['descripcion'],
                monto_modificacion=row['monto_modificacion'],
                fecha_modificacion=row['fecha_modificacion'],
                usuario_autoriza_id=row['usuario_autoriza_id'],
                estado=row['estado'],
                fecha_creacion=row['fecha_creacion']
            ))
        return suplementos
    
    @classmethod
    def get_all(cls):
        """Obtiene todos los suplementos"""
        query = "SELECT * FROM suplementos ORDER BY fecha_creacion DESC"
        results = db_manager.execute_query(query)
        suplementos = []
        for row in results:
            suplementos.append(cls(
                id=row['id'],
                contrato_id=row['contrato_id'],
                numero_suplemento=row['numero_suplemento'],
                tipo_modificacion=row['tipo_modificacion'],
                descripcion=row['descripcion'],
                monto_modificacion=row['monto_modificacion'],
                fecha_modificacion=row['fecha_modificacion'],
                usuario_autoriza_id=row['usuario_autoriza_id'],
                estado=row['estado'],
                fecha_creacion=row['fecha_creacion']
            ))
        return suplementos