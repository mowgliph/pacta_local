from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Usuario:
    def __init__(self, id=None, nombre=None, email=None, username=None, password=None, telefono=None, cargo=None, departamento=None, es_admin=False, fecha_creacion=None, activo=True):
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
    
    def save(self):
        """Guarda o actualiza el usuario en la base de datos"""
        if self.id:
            # Actualizar usuario existente
            query = '''
                UPDATE usuarios 
                SET nombre=?, email=?, username=?, password=?, telefono=?, cargo=?, departamento=?, es_admin=?, activo=?
                WHERE id=?
            '''
            params = (self.nombre, self.email, self.username, self.password, self.telefono, self.cargo, self.departamento, self.es_admin, self.activo, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo usuario
            query = '''
                INSERT INTO usuarios (nombre, email, username, password, telefono, cargo, departamento, es_admin, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.nombre, self.email, self.username, self.password, self.telefono, self.cargo, self.departamento, self.es_admin, self.activo)
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
                activo=row['activo']
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
                activo=row['activo']
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
                activo=row['activo']
            ))
        return usuarios

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

class Contrato:
    def __init__(self, id=None, numero_contrato=None, cliente_id=None, usuario_responsable_id=None, titulo=None, descripcion=None, monto_original=None, monto_actual=None, fecha_inicio=None, fecha_fin=None, estado='borrador', tipo_contrato=None, fecha_creacion=None, fecha_modificacion=None):
        self.id = id
        self.numero_contrato = numero_contrato
        self.cliente_id = cliente_id
        self.usuario_responsable_id = usuario_responsable_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.monto_original = monto_original
        self.monto_actual = monto_actual
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.tipo_contrato = tipo_contrato
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
    
    def save(self):
        """Guarda o actualiza el contrato en la base de datos"""
        if self.id:
            # Actualizar contrato existente
            query = '''
                UPDATE contratos 
                SET numero_contrato=?, cliente_id=?, usuario_responsable_id=?, titulo=?, descripcion=?, 
                    monto_original=?, monto_actual=?, fecha_inicio=?, fecha_fin=?, estado=?, 
                    tipo_contrato=?, fecha_modificacion=CURRENT_TIMESTAMP
                WHERE id=?
            '''
            params = (self.numero_contrato, self.cliente_id, self.usuario_responsable_id, self.titulo, 
                     self.descripcion, self.monto_original, self.monto_actual, self.fecha_inicio, 
                     self.fecha_fin, self.estado, self.tipo_contrato, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo contrato
            query = '''
                INSERT INTO contratos (numero_contrato, cliente_id, usuario_responsable_id, titulo, descripcion, 
                                     monto_original, monto_actual, fecha_inicio, fecha_fin, estado, tipo_contrato)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.numero_contrato, self.cliente_id, self.usuario_responsable_id, self.titulo, 
                     self.descripcion, self.monto_original, self.monto_actual, self.fecha_inicio, 
                     self.fecha_fin, self.estado, self.tipo_contrato)
            self.id = db_manager.execute_insert(query, params)
        return self
    
    @classmethod
    def get_by_id(cls, contrato_id):
        """Obtiene un contrato por su ID"""
        query = "SELECT * FROM contratos WHERE id = ?"
        result = db_manager.execute_query(query, (contrato_id,))
        if result:
            row = result[0]
            return cls(
                id=row['id'],
                numero_contrato=row['numero_contrato'],
                cliente_id=row['cliente_id'],
                usuario_responsable_id=row['usuario_responsable_id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                monto_original=row['monto_original'],
                monto_actual=row['monto_actual'],
                fecha_inicio=row['fecha_inicio'],
                fecha_fin=row['fecha_fin'],
                estado=row['estado'],
                tipo_contrato=row['tipo_contrato'],
                fecha_creacion=row['fecha_creacion'],
                fecha_modificacion=row['fecha_modificacion']
            )
        return None
    
    @classmethod
    def get_all(cls, estado=None):
        """Obtiene todos los contratos, opcionalmente filtrados por estado"""
        query = "SELECT * FROM contratos"
        params = []
        
        if estado:
            query += " WHERE estado = ?"
            params.append(estado)
        
        query += " ORDER BY fecha_creacion DESC"
        
        results = db_manager.execute_query(query, params if params else None)
        contratos = []
        for row in results:
            contratos.append(cls(
                id=row['id'],
                numero_contrato=row['numero_contrato'],
                cliente_id=row['cliente_id'],
                usuario_responsable_id=row['usuario_responsable_id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                monto_original=row['monto_original'],
                monto_actual=row['monto_actual'],
                fecha_inicio=row['fecha_inicio'],
                fecha_fin=row['fecha_fin'],
                estado=row['estado'],
                tipo_contrato=row['tipo_contrato'],
                fecha_creacion=row['fecha_creacion'],
                fecha_modificacion=row['fecha_modificacion']
            ))
        return contratos

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