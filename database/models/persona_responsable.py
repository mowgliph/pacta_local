from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class PersonaResponsable:
    def __init__(self, id=None, cliente_id=None, nombre=None, cargo=None, telefono=None, email=None, es_principal=False, fecha_creacion=None, activo=True, documento_path=None, observaciones=None):
        self.id = id
        self.cliente_id = cliente_id
        self.nombre = nombre
        self.cargo = cargo
        self.telefono = telefono
        self.email = email
        self.es_principal = es_principal
        self.fecha_creacion = fecha_creacion
        self.activo = activo
        self.documento_path = documento_path
        self.observaciones = observaciones
    
    def save(self):
        """Guarda o actualiza la persona responsable en la base de datos"""
        if self.id:
            # Actualizar persona existente
            query = '''
                UPDATE personas_responsables 
                SET cliente_id=?, nombre=?, cargo=?, telefono=?, email=?, es_principal=?, activo=?, documento_path=?, observaciones=?
                WHERE id=?
            '''
            params = (self.cliente_id, self.nombre, self.cargo, self.telefono, self.email, self.es_principal, self.activo, self.documento_path, self.observaciones, self.id)
            db_manager.execute_update(query, params)
            return self.id
        else:
            # Crear nueva persona
            query = '''
                INSERT INTO personas_responsables (cliente_id, nombre, cargo, telefono, email, es_principal, activo, documento_path, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.cliente_id, self.nombre, self.cargo, self.telefono, self.email, self.es_principal, self.activo, self.documento_path, self.observaciones)
            self.id = db_manager.execute_insert(query, params)
            return self.id
    
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
                activo=row['activo'],
                documento_path=row['documento_path'] if 'documento_path' in row.keys() else None,
                observaciones=row['observaciones'] if 'observaciones' in row.keys() else None
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
                activo=row['activo'],
                documento_path=row['documento_path'] if 'documento_path' in row.keys() else None,
                observaciones=row['observaciones'] if 'observaciones' in row.keys() else None
            ))
        return personas
    
    def delete(self):
        """Elimina la persona responsable de la base de datos (eliminación física)"""
        if not self.id:
            raise ValueError("No se puede eliminar una persona sin ID")
        
        # Eliminar archivo de documento si existe
        if self.documento_path and os.path.exists(self.documento_path):
            try:
                os.remove(self.documento_path)
            except Exception as e:
                print(f"Error al eliminar documento: {e}")
        
        # Eliminación física: borrar completamente de la base de datos
        query = "DELETE FROM personas_responsables WHERE id = ?"
        db_manager.execute_update(query, (self.id,))
        return True
    
    @classmethod
    def delete_by_id(cls, persona_id):
        """Elimina una persona por su ID (eliminación física)"""
        # Primero obtener la persona para eliminar su documento
        persona = cls.get_by_id(persona_id)
        if persona:
            return persona.delete()
        return False

    @classmethod
    def get_by_ids(cls, ids):
        """Obtiene personas responsables por lista de IDs"""
        if not ids:
            return []
        
        # Crear placeholders para la consulta IN
        placeholders = ','.join(['?' for _ in ids])
        query = f"SELECT * FROM personas_responsables WHERE id IN ({placeholders}) AND activo = 1 ORDER BY nombre"
        
        results = db_manager.execute_query(query, ids)
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
                activo=row['activo'],
                documento_path=row['documento_path'] if 'documento_path' in row.keys() else None,
                observaciones=row['observaciones'] if 'observaciones' in row.keys() else None
            ))
        return personas
    
    @classmethod
    def search(cls, search_term, activos_solo=True):
        """Busca personas responsables por nombre, cargo o email"""
        if not search_term:
            return []
        
        search_term = f"%{search_term.strip()}%"
        query = """
            SELECT * FROM personas_responsables 
            WHERE (nombre LIKE ? OR cargo LIKE ? OR email LIKE ?)
        """
        params = [search_term, search_term, search_term]
        
        if activos_solo:
            query += " AND activo = 1"
        
        query += " ORDER BY nombre LIMIT 20"
        
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
                activo=row['activo'],
                documento_path=row['documento_path'] if 'documento_path' in row.keys() else None,
                observaciones=row['observaciones'] if 'observaciones' in row.keys() else None
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
                activo=row['activo'],
                documento_path=row['documento_path'] if 'documento_path' in row.keys() else None,
                observaciones=row['observaciones'] if 'observaciones' in row.keys() else None
            ))
        return personas