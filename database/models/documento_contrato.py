from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class DocumentoContrato:
    def __init__(self, id=None, contrato_id=None, nombre_archivo=None, ruta_archivo=None, tipo_documento=None, tamaño_archivo=None, fecha_subida=None, usuario_subida_id=None):
        self.id = id
        self.contrato_id = contrato_id
        self.nombre_archivo = nombre_archivo
        self.ruta_archivo = ruta_archivo
        self.tipo_documento = tipo_documento
        self.tamaño_archivo = tamaño_archivo
        self.fecha_subida = fecha_subida
        self.usuario_subida_id = usuario_subida_id
    
    def save(self):
        """Guarda el documento en la base de datos"""
        if self.id:
            # Actualizar documento existente
            query = '''
                UPDATE documentos_contratos 
                SET contrato_id=?, nombre_archivo=?, ruta_archivo=?, tipo_documento=?, tamaño_archivo=?
                WHERE id=?
            '''
            params = (self.contrato_id, self.nombre_archivo, self.ruta_archivo, self.tipo_documento, self.tamaño_archivo, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo documento
            query = '''
                INSERT INTO documentos_contratos (contrato_id, nombre_archivo, ruta_archivo, tipo_documento, tamaño_archivo, usuario_subida_id)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (self.contrato_id, self.nombre_archivo, self.ruta_archivo, self.tipo_documento, self.tamaño_archivo, self.usuario_subida_id)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_contrato(cls, contrato_id):
        """Obtiene todos los documentos de un contrato"""
        query = "SELECT * FROM documentos_contratos WHERE contrato_id = ? ORDER BY fecha_subida DESC"
        results = db_manager.execute_query(query, (contrato_id,))
        documentos = []
        for row in results:
            documentos.append(cls(
                id=row['id'],
                contrato_id=row['contrato_id'],
                nombre_archivo=row['nombre_archivo'],
                ruta_archivo=row['ruta_archivo'],
                tipo_documento=row['tipo_documento'],
                tamaño_archivo=row['tamaño_archivo'],
                fecha_subida=row['fecha_subida'],
                usuario_subida_id=row['usuario_subida_id']
            ))
        return documentos
    
    @classmethod
    def get_by_id(cls, documento_id):
        """Obtiene un documento por su ID"""
        query = "SELECT * FROM documentos_contratos WHERE id = ?"
        result = db_manager.execute_query(query, (documento_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                contrato_id=row['contrato_id'],
                nombre_archivo=row['nombre_archivo'],
                ruta_archivo=row['ruta_archivo'],
                tipo_documento=row['tipo_documento'],
                tamaño_archivo=row['tamaño_archivo'],
                fecha_subida=row['fecha_subida'],
                usuario_subida_id=row['usuario_subida_id']
            )
        return None
    
    def delete(self):
        """Elimina el documento de la base de datos"""
        if self.id:
            query = "DELETE FROM documentos_contratos WHERE id = ?"
            db_manager.execute_update(query, (self.id,))
            return True
        return False