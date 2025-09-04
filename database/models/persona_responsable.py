from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class PersonaResponsable:
    def __init__(self, id=None, cliente_id=None, nombre=None, cargo=None, telefono=None, email=None, es_principal=False, fecha_creacion=None, activo=True):
        self.id = id
        self.cliente_id = cliente_id
        self.nombre = nombre
        self.cargo = cargo
        self.telefono = telefono
        self.email = email
        self.es_principal = es_principal
        self.fecha_creacion = fecha_creacion
        self.activo = activo
    
    def save(self):
        """Guarda o actualiza la persona responsable en la base de datos"""
        if self.id:
            # Actualizar persona existente
            query = '''
                UPDATE personas_responsables 
                SET cliente_id=?, nombre=?, cargo=?, telefono=?, email=?, es_principal=?, activo=?
                WHERE id=?
            '''
            params = (self.cliente_id, self.nombre, self.cargo, self.telefono, self.email, self.es_principal, self.activo, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nueva persona
            query = '''
                INSERT INTO personas_responsables (cliente_id, nombre, cargo, telefono, email, es_principal, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.cliente_id, self.nombre, self.cargo, self.telefono, self.email, self.es_principal, self.activo)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_id(cls, persona_id):
        """Obtiene una persona responsable por su ID"""
        query = "SELECT * FROM personas_responsables WHERE id = ?"
        result = db_manager.execute_query(query, (persona_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                cliente_id=row['cliente_id'],
                nombre=row['nombre'],
                cargo=row['cargo'],
                telefono=row['telefono'],
                email=row['email'],
                es_principal=row['es_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            )
        return None
    
    @classmethod
    def get_by_cliente(cls, cliente_id, activos_solo=True):
        """Obtiene todas las personas responsables de un cliente"""
        query = "SELECT * FROM personas_responsables WHERE cliente_id = ?"
        params = [cliente_id]
        
        if activos_solo:
            query += " AND activo = 1"
        
        query += " ORDER BY es_principal DESC, nombre"
        
        results = db_manager.execute_query(query, params)
        personas = []
        for row in results:
            personas.append(cls(
                id=row['id'],
                cliente_id=row['cliente_id'],
                nombre=row['nombre'],
                cargo=row['cargo'],
                telefono=row['telefono'],
                email=row['email'],
                es_principal=row['es_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            ))
        return personas
    
    @classmethod
    def get_all(cls, activos_solo=True):
        """Obtiene todas las personas responsables"""
        query = "SELECT * FROM personas_responsables"
        params = []
        
        if activos_solo:
            query += " WHERE activo = 1"
        
        query += " ORDER BY nombre"
        
        results = db_manager.execute_query(query, params if params else None)
        personas = []
        for row in results:
            personas.append(cls(
                id=row['id'],
                cliente_id=row['cliente_id'],
                nombre=row['nombre'],
                cargo=row['cargo'],
                telefono=row['telefono'],
                email=row['email'],
                es_principal=row['es_principal'],
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo']
            ))
        return personas