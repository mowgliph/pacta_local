from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Cliente:
    def __init__(self, id=None, nombre=None, tipo_cliente=None, rfc=None, direccion=None, telefono=None, email=None, contacto_principal=None, fecha_creacion=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.tipo_cliente = tipo_cliente  # 'cliente' o 'proveedor'
        self.rfc = rfc
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.contacto_principal = contacto_principal
        self.fecha_creacion = fecha_creacion
        self.activo = activo
    
    def save(self):
        """Guarda o actualiza el cliente en la base de datos"""
        if self.id:
            # Actualizar cliente existente
            query = '''
                UPDATE clientes 
                SET nombre=?, tipo_cliente=?, rfc=?, direccion=?, telefono=?, email=?, contacto_principal=?, activo=?
                WHERE id=?
            '''
            params = (self.nombre, self.tipo_cliente, self.rfc, self.direccion, self.telefono, self.email, self.contacto_principal, self.activo, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo cliente
            query = '''
                INSERT INTO clientes (nombre, tipo_cliente, rfc, direccion, telefono, email, contacto_principal, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.nombre, self.tipo_cliente, self.rfc, self.direccion, self.telefono, self.email, self.contacto_principal, self.activo)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_id(cls, cliente_id):
        """Obtiene un cliente por su ID"""
        query = "SELECT * FROM clientes WHERE id = ?"
        result = db_manager.execute_query(query, (cliente_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                nombre=row['nombre'],
                tipo_cliente=row['tipo_cliente'],
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
    def get_by_tipo(cls, tipo_cliente, activos_solo=True):
        """Obtiene clientes por tipo (cliente o proveedor)"""
        query = "SELECT * FROM clientes WHERE tipo_cliente = ?"
        params = [tipo_cliente]
        
        if activos_solo:
            query += " AND activo = 1"
        
        query += " ORDER BY nombre"
        
        results = db_manager.execute_query(query, params)
        clientes = []
        for row in results:
            clientes.append(cls(
                id=row['id'],
                nombre=row['nombre'],
                tipo_cliente=row['tipo_cliente'],
                rfc=row['rfc'],
                direccion=row['direccion'],
                telefono=row['telefono'],
                email=row['email'],
                contacto_principal=row['contacto_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            ))
        return clientes