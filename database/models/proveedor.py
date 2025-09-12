from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Proveedor:
    def __init__(self, id=None, nombre=None, tipo_proveedor=None, rfc=None, direccion=None, telefono=None, email=None, contacto_principal=None, fecha_creacion=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.tipo_proveedor = tipo_proveedor
        self.rfc = rfc
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.contacto_principal = contacto_principal
        self.fecha_creacion = fecha_creacion
        self.activo = activo
    
    def save(self):
        """Guarda o actualiza el proveedor en la base de datos"""
        if self.id:
            # Actualizar proveedor existente
            query = '''
                UPDATE proveedores 
                SET nombre=?, tipo_proveedor=?, rfc=?, direccion=?, telefono=?, email=?, contacto_principal=?, activo=?
                WHERE id=?
            '''
            params = (self.nombre, self.tipo_proveedor, self.rfc, self.direccion, self.telefono, self.email, self.contacto_principal, self.activo, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo proveedor
            query = '''
                INSERT INTO proveedores (nombre, tipo_proveedor, rfc, direccion, telefono, email, contacto_principal, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.nombre, self.tipo_proveedor, self.rfc, self.direccion, self.telefono, self.email, self.contacto_principal, self.activo)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_id(cls, proveedor_id):
        """Obtiene un proveedor por su ID"""
        query = "SELECT * FROM proveedores WHERE id = ?"
        result = db_manager.execute_query(query, (proveedor_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                nombre=row['nombre'],
                tipo_proveedor=row['tipo_proveedor'],
                rfc=row['rfc'],
                direccion=row['direccion'],
                telefono=row['telefono'],
                email=row['email'],
                contacto_principal=row['contacto_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            )
        return None
    
    @classmethod
    def get_by_tipo(cls, tipo_proveedor, activos_solo=True):
        """Obtiene proveedores por tipo"""
        query = "SELECT * FROM proveedores WHERE tipo_proveedor = ?"
        params = [tipo_proveedor]
        
        if activos_solo:
            query += " AND activo = 1"
        
        query += " ORDER BY nombre"
        
        results = db_manager.execute_query(query, params)
        proveedores = []
        for row in results:
            proveedores.append(cls(
                id=row['id'],
                nombre=row['nombre'],
                tipo_proveedor=row['tipo_proveedor'],
                rfc=row['rfc'],
                direccion=row['direccion'],
                telefono=row['telefono'],
                email=row['email'],
                contacto_principal=row['contacto_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            ))
        return proveedores
    
    def delete(self):
        """Elimina físicamente el proveedor de la base de datos"""
        if self.id:
            query = "DELETE FROM proveedores WHERE id = ?"
            db_manager.execute_update(query, (self.id,))
            return True
        return False
    
    @classmethod
    def get_all(cls, activos_solo=True):
        """Obtiene todos los proveedores"""
        query = "SELECT * FROM proveedores"
        params = []
        
        if activos_solo:
            query += " WHERE activo = 1"
        
        query += " ORDER BY nombre"
        
        results = db_manager.execute_query(query, params)
        proveedores = []
        for row in results:
            proveedores.append(cls(
                id=row['id'],
                nombre=row['nombre'],
                tipo_proveedor=row['tipo_proveedor'],
                rfc=row['rfc'],
                direccion=row['direccion'],
                telefono=row['telefono'],
                email=row['email'],
                contacto_principal=row['contacto_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            ))
        return proveedores