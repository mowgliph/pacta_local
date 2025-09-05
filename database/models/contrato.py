from datetime import datetime, date
import sys
import os

# Agregar el directorio database al path si no está
database_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from database import db_manager

class Contrato:
    def __init__(self, id=None, numero_contrato=None, cliente_id=None, usuario_responsable_id=None, persona_responsable_id=None, titulo=None, descripcion=None, monto_original=None, monto_actual=None, fecha_inicio=None, fecha_fin=None, estado='borrador', tipo_contrato=None, fecha_creacion=None, fecha_modificacion=None):
        self.id = id
        self.numero_contrato = numero_contrato
        self.cliente_id = cliente_id
        self.usuario_responsable_id = usuario_responsable_id
        self.persona_responsable_id = persona_responsable_id
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
                SET numero_contrato=?, cliente_id=?, usuario_responsable_id=?, persona_responsable_id=?, titulo=?, descripcion=?, 
                    monto_original=?, monto_actual=?, fecha_inicio=?, fecha_fin=?, estado=?, 
                    tipo_contrato=?, fecha_modificacion=CURRENT_TIMESTAMP
                WHERE id=?
            '''
            params = (self.numero_contrato, self.cliente_id, self.usuario_responsable_id, self.persona_responsable_id, self.titulo, 
                     self.descripcion, self.monto_original, self.monto_actual, self.fecha_inicio, 
                     self.fecha_fin, self.estado, self.tipo_contrato, self.id)
            db_manager.execute_update(query, params)
        else:
            # Crear nuevo contrato
            query = '''
                INSERT INTO contratos (numero_contrato, cliente_id, usuario_responsable_id, persona_responsable_id, titulo, descripcion, 
                                     monto_original, monto_actual, fecha_inicio, fecha_fin, estado, tipo_contrato)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (self.numero_contrato, self.cliente_id, self.usuario_responsable_id, self.persona_responsable_id, self.titulo, 
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
                persona_responsable_id=row['persona_responsable_id'] if 'persona_responsable_id' in row.keys() else None,
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
                persona_responsable_id=row['persona_responsable_id'] if 'persona_responsable_id' in row.keys() else None,
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
    
    @classmethod
    def get_by_cliente(cls, cliente_id, estado=None):
        """Obtiene todos los contratos de un cliente específico"""
        query = "SELECT * FROM contratos WHERE cliente_id = ?"
        params = [cliente_id]
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY fecha_creacion DESC"
        
        results = db_manager.execute_query(query, params)
        contratos = []
        for row in results:
            contratos.append(cls(
                id=row['id'],
                numero_contrato=row['numero_contrato'],
                cliente_id=row['cliente_id'],
                usuario_responsable_id=row['usuario_responsable_id'],
                persona_responsable_id=row['persona_responsable_id'] if 'persona_responsable_id' in row.keys() else None,
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
    
    @classmethod
    def search(cls, search_term, cliente_id=None, estado=None):
        """Busca contratos por número, título o descripción"""
        query = """SELECT * FROM contratos 
                   WHERE (numero_contrato LIKE ? OR titulo LIKE ? OR descripcion LIKE ?)"""
        params = [f'%{search_term}%', f'%{search_term}%', f'%{search_term}%']
        
        if cliente_id:
            query += " AND cliente_id = ?"
            params.append(cliente_id)
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY fecha_creacion DESC"
        
        results = db_manager.execute_query(query, params)
        contratos = []
        for row in results:
            contratos.append(cls(
                id=row['id'],
                numero_contrato=row['numero_contrato'],
                cliente_id=row['cliente_id'],
                usuario_responsable_id=row['usuario_responsable_id'],
                persona_responsable_id=row.get('persona_responsable_id'),
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
    
    def delete(self):
        """Elimina el contrato de la base de datos"""
        if self.id:
            query = "DELETE FROM contratos WHERE id = ?"
            db_manager.execute_update(query, (self.id,))
            return True
        return False
    
    def get_cliente(self):
        """Obtiene el cliente asociado al contrato"""
        if self.cliente_id:
            from .cliente import Cliente
            return Cliente.get_by_id(self.cliente_id)
        return None
    
    def get_persona_responsable(self):
        """Obtiene la persona responsable asociada al contrato"""
        if self.persona_responsable_id:
            from .persona_responsable import PersonaResponsable
            return PersonaResponsable.get_by_id(self.persona_responsable_id)
        return None
    
    def get_documentos(self):
        """Obtiene todos los documentos asociados al contrato"""
        from .documento_contrato import DocumentoContrato
        return DocumentoContrato.get_by_contrato(self.id)
    
    def get_suplementos(self):
        """Obtiene todos los suplementos asociados al contrato"""
        from .suplemento import Suplemento
        return Suplemento.get_by_contrato(self.id)
    
    @staticmethod
    def get_expired_contracts():
        """Obtiene todos los contratos vencidos"""
        query = '''
            SELECT * FROM contratos 
            WHERE fecha_fin < date('now') 
            AND estado IN ('activo', 'vigente')
            ORDER BY fecha_fin ASC
        '''
        rows = db_manager.execute_query(query)
        contratos = []
        for row in rows:
            contrato = Contrato(
                id=row[0], numero_contrato=row[1], cliente_id=row[2], usuario_responsable_id=row[3],
                persona_responsable_id=None, titulo=row[4], descripcion=row[5], monto_original=row[6],
                monto_actual=row[7], fecha_inicio=row[8], fecha_fin=row[9], estado=row[10],
                tipo_contrato=row[11], fecha_creacion=row[12], fecha_modificacion=row[13]
            )
            # Convertir fecha_fin de string a date si es necesario
            if isinstance(contrato.fecha_fin, str):
                try:
                    contrato.fecha_fin = datetime.strptime(contrato.fecha_fin, '%Y-%m-%d').date()
                except ValueError:
                    contrato.fecha_fin = None
            contratos.append(contrato)
        return contratos