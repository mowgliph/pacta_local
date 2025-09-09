from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Usuario:
    def __init__(self, id=None, nombre=None, email=None, username=None, password=None, telefono=None, cargo=None, departamento=None, es_admin=False, fecha_creacion=None, activo=True, rol='user'):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.username = username
        self.password = password
        self.telefono = telefono
        self.cargo = cargo
        self.departamento = departamento
        self.es_admin = es_admin
        self.fecha_creacion = fecha_creacion
        self.activo = activo
        self.rol = rol  # 'admin', 'user', 'guest', 'viewer'
    
    def save(self):
        """Guarda o actualiza el usuario en la base de datos"""
        if self.id:
            # Actualizar usuario existente
            query = '''
                UPDATE usuarios 
                SET nombre=?, email=?, username=?, password=?, telefono=?, cargo=?, departamento=?, es_admin=?, activo=?, rol=?
                WHERE id=?
            '''
            params = (self.nombre, self.email, self.username, self.password, self.telefono, self.cargo, self.departamento, self.es_admin, self.activo, self.rol, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo usuario
            query = '''
                INSERT INTO usuarios (nombre, email, username, password, telefono, cargo, departamento, es_admin, activo, rol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.nombre, self.email, self.username, self.password, self.telefono, self.cargo, self.departamento, self.es_admin, self.activo, self.rol)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        """Obtiene un usuario por su ID"""
        query = "SELECT * FROM usuarios WHERE id = ?"
        result = db_manager.execute_query(query, (user_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                nombre=row['nombre'],
                email=row['email'],
                username=row['username'] if 'username' in row.keys() else None,
                password=row['password'] if 'password' in row.keys() else None,
                telefono=row['telefono'],
                cargo=row['cargo'],
                departamento=row['departamento'],
                es_admin=row['es_admin'] if 'es_admin' in row.keys() else False,
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo'],
                rol=row['rol'] if 'rol' in row.keys() else 'user'
            )
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """Obtiene un usuario por su username"""
        query = "SELECT * FROM usuarios WHERE username = ? AND activo = 1"
        result = db_manager.execute_query(query, (username,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                nombre=row['nombre'],
                email=row['email'],
                username=row['username'] if 'username' in row.keys() else None,
                password=row['password'] if 'password' in row.keys() else None,
                telefono=row['telefono'],
                cargo=row['cargo'],
                departamento=row['departamento'],
                es_admin=row['es_admin'] if 'es_admin' in row.keys() else False,
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo'],
                rol=row['rol'] if 'rol' in row.keys() else 'user'
            )
        return None
    
    def verificar_password(self, password):
        """Verifica si la contraseña proporcionada es correcta"""
        # Por simplicidad, comparación directa. En producción usar hashing
        return self.password == password
    
    @staticmethod
    def hash_password(password):
        """Hash de contraseña (implementación simple, en producción usar bcrypt)"""
        # Por simplicidad, retornamos la contraseña tal como está
        # En producción se debería usar bcrypt o similar
        return password
    
    @classmethod
    def get_all(cls, activos_solo=True):
        """Obtiene todos los usuarios"""
        query = "SELECT * FROM usuarios"
        if activos_solo:
            query += " WHERE activo = 1"
        query += " ORDER BY nombre"
        
        results = db_manager.execute_query(query)
        usuarios = []
        for row in results:
            usuarios.append(cls(
                id=row['id'],
                nombre=row['nombre'],
                email=row['email'],
                username=row['username'] if 'username' in row.keys() else None,
                password=row['password'] if 'password' in row.keys() else None,
                telefono=row['telefono'],
                cargo=row['cargo'],
                departamento=row['departamento'],
                es_admin=row['es_admin'] if 'es_admin' in row.keys() else False,
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo'],
                rol=row['rol'] if 'rol' in row.keys() else 'user'
            ))
        return usuarios
    
    @classmethod
    def get_recent(cls, limit=10, activos_solo=True):
        """Obtiene los usuarios más recientes por fecha de creación"""
        query = "SELECT * FROM usuarios"
        if activos_solo:
            query += " WHERE activo = 1"
        query += " ORDER BY fecha_creacion DESC LIMIT ?"
        
        results = db_manager.execute_query(query, (limit,))
        usuarios = []
        for row in results:
            usuarios.append(cls(
                id=row['id'],
                nombre=row['nombre'],
                email=row['email'],
                username=row['username'] if 'username' in row.keys() else None,
                password=row['password'] if 'password' in row.keys() else None,
                telefono=row['telefono'],
                cargo=row['cargo'],
                departamento=row['departamento'],
                es_admin=row['es_admin'] if 'es_admin' in row.keys() else False,
                fecha_creacion=row['fecha_creacion'],
                activo=row['activo'],
                rol=row['rol'] if 'rol' in row.keys() else 'user'
            ))
        return usuarios
    
    def delete(self):
        """Elimina el usuario de la base de datos (eliminación física)"""
        if not self.id:
            raise ValueError("No se puede eliminar un usuario sin ID")
        
        # Eliminación física: borrar completamente de la base de datos
        query = "DELETE FROM usuarios WHERE id = ?"
        db_manager.execute_update(query, (self.id,))
        return True
    
    @classmethod
    def delete_by_id(cls, user_id):
        """Elimina un usuario por su ID (eliminación física)"""
        query = "DELETE FROM usuarios WHERE id = ?"
        db_manager.execute_update(query, (user_id,))
        return True