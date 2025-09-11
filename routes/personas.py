from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from database.models import PersonaResponsable, Cliente, Notificacion, Usuario
from database.database import DatabaseManager
import logging
import os
from werkzeug.utils import secure_filename

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia del gestor de base de datos
db_manager = DatabaseManager()

# Crear blueprint para personas responsables
personas_bp = Blueprint('personas', __name__, url_prefix='/personas')

# Función helper para obtener contador de notificaciones
def get_notificaciones_count():
    """Obtiene el número de notificaciones no leídas del usuario actual"""
    if 'user_id' in session:
        return Notificacion.get_unread_count(session['user_id'])
    return 0

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@personas_bp.route('/')
@login_required
def listar_personas():
    """Mostrar lista de todas las personas responsables"""
    try:
        # Obtener todas las personas responsables
        personas = PersonaResponsable.get_all()
        
        # Obtener todos los clientes para el formulario
        clientes = Cliente.get_all()
        
        # Calcular estadísticas
        total_personas = len(personas)
        personas_activas = len([p for p in personas if p.activo])
        personas_principales = len([p for p in personas if p.es_principal])
        clientes_con_personas = len(set([p.cliente_id for p in personas if p.cliente_id is not None]))
        
        estadisticas = {
            'total_personas': total_personas,
            'personas_activas': personas_activas,
            'personas_principales': personas_principales,
            'clientes_con_personas': clientes_con_personas,
            'porcentaje_activas': round((personas_activas / total_personas * 100) if total_personas > 0 else 0, 1),
            'porcentaje_principales': round((personas_principales / total_personas * 100) if total_personas > 0 else 0, 1)
        }
        
        # Obtener usuario actual y contador de notificaciones
        usuario = Usuario.get_by_id(session['user_id'])
        notificaciones_count = get_notificaciones_count()
        
        return render_template('personas/listar.html', 
                             personas=personas,
                             clientes=clientes,
                             estadisticas=estadisticas,
                             usuario=usuario,
                             notificaciones_count=notificaciones_count)
    except Exception as e:
        logger.error(f"Error al listar personas: {e}")
        flash('Error al cargar la lista de personas', 'error')
        return redirect(url_for('main.dashboard'))

@personas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_persona():
    """Crear nueva persona responsable"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            if not nombre:
                return jsonify({'success': False, 'message': 'El nombre es un campo obligatorio'}), 400
            
            # Obtener cliente_id (opcional ahora)
            cliente_id = request.form.get('cliente_id')
            if cliente_id:
                cliente_id = int(cliente_id)
            else:
                cliente_id = None
            
            # Manejar archivo de documento
            documento_path = None
            if 'documento' in request.files:
                file = request.files['documento']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Crear directorio si no existe
                    upload_folder = os.path.join('static', 'uploads', 'documentos')
                    os.makedirs(upload_folder, exist_ok=True)
                    # Guardar archivo
                    documento_path = os.path.join(upload_folder, filename)
                    file.save(documento_path)
            
            # Si es principal y tiene cliente, desactivar otros principales del mismo cliente
            es_principal_value = request.form.get('es_principal')
            es_principal = es_principal_value in ['true', 'True', '1', 'on', True]
            if es_principal and cliente_id:
                db_manager.execute_update(
                    "UPDATE personas_responsables SET es_principal = 0 WHERE cliente_id = ?",
                    (cliente_id,)
                )
            
            # Crear nueva persona
            persona = PersonaResponsable(
                cliente_id=cliente_id,
                nombre=nombre,
                cargo=request.form.get('cargo'),
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
                es_principal=es_principal,
                activo=request.form.get('activo', 'true').lower() == 'true',
                documento_path=documento_path,
                observaciones=request.form.get('observaciones')
            )
            
            persona_id = persona.save()
            
            if persona_id:
                return jsonify({'success': True, 'message': 'Persona responsable creada exitosamente', 'id': persona_id})
            else:
                return jsonify({'success': False, 'message': 'Error al crear la persona responsable'}), 500
                
        except Exception as e:
            logger.error(f"Error al crear persona: {e}")
            return jsonify({'success': False, 'message': 'Error al crear la persona responsable'}), 500
    
    # Obtener lista de clientes para el formulario
    try:
        clientes = Cliente.get_all()
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        return render_template('personas/crear.html', clientes=clientes, notificaciones_count=notificaciones_count)
    except Exception as e:
        logger.error(f"Error al cargar clientes: {e}")
        flash('Error al cargar la lista de clientes', 'error')
        return redirect(url_for('personas.listar_personas'))

@personas_bp.route('/editar/<int:persona_id>', methods=['GET', 'POST'])
@login_required
def editar_persona(persona_id):
    """Editar persona responsable existente"""
    try:
        persona = PersonaResponsable.get_by_id(persona_id)
        if not persona:
            return jsonify({'success': False, 'message': 'Persona no encontrada'}), 404
        
        if request.method == 'POST':
            # Obtener datos del formulario (FormData)
            nombre = request.form.get('nombre')
            if not nombre:
                return jsonify({'success': False, 'message': 'El nombre es obligatorio'}), 400
            
            # Obtener cliente_id (opcional)
            cliente_id = request.form.get('cliente_id')
            if cliente_id:
                cliente_id = int(cliente_id)
            else:
                cliente_id = None
            
            # Manejar archivo de documento
            documento_path = persona.documento_path  # Mantener el documento actual por defecto
            if 'documento' in request.files:
                file = request.files['documento']
                if file and file.filename != '':
                    # Eliminar documento anterior si existe
                    if persona.documento_path and os.path.exists(persona.documento_path):
                        try:
                            os.remove(persona.documento_path)
                            logger.info(f"Documento anterior eliminado: {persona.documento_path}")
                        except Exception as e:
                            logger.warning(f"No se pudo eliminar el documento anterior: {e}")
                    
                    # Guardar nuevo documento
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join('static', 'uploads', 'documentos')
                    os.makedirs(upload_folder, exist_ok=True)
                    documento_path = os.path.join(upload_folder, filename)
                    file.save(documento_path)
            
            # Si es principal, desactivar otros principales del mismo cliente
            es_principal_value = request.form.get('es_principal')
            es_principal = es_principal_value in ['true', 'True', '1', 'on', True]
            if es_principal and not persona.es_principal and cliente_id:
                db_manager.execute_update(
                    "UPDATE personas_responsables SET es_principal = 0 WHERE cliente_id = ? AND id != ?",
                    (cliente_id, persona_id)
                )
            
            # Actualizar datos de la persona
            persona.nombre = nombre
            persona.cliente_id = cliente_id
            persona.cargo = request.form.get('cargo')
            persona.telefono = request.form.get('telefono')
            persona.email = request.form.get('email')
            persona.es_principal = es_principal
            persona.activo = request.form.get('activo', 'true').lower() == 'true'
            persona.documento_path = documento_path
            persona.observaciones = request.form.get('observaciones')
            
            # Guardar cambios
            if persona.save():
                return jsonify({'success': True, 'message': 'Persona actualizada exitosamente'})
            else:
                return jsonify({'success': False, 'message': 'Error al actualizar la persona'}), 500
        
        # GET request - devolver datos de la persona
        return jsonify({
            'success': True,
            'persona': {
                'id': persona.id,
                'nombre': persona.nombre,
                'cliente_id': persona.cliente_id,
                'cargo': persona.cargo,
                'telefono': persona.telefono,
                'email': persona.email,
                'es_principal': persona.es_principal,
                'activo': persona.activo,
                'documento_path': persona.documento_path,
                'observaciones': persona.observaciones
            }
        })
        
    except Exception as e:
        logger.error(f"Error al editar persona: {e}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'}), 500

@personas_bp.route('/eliminar/<int:persona_id>', methods=['POST'])
@login_required
def eliminar_persona(persona_id):
    """Eliminar persona responsable completamente"""
    try:
        persona = PersonaResponsable.get_by_id(persona_id)
        if not persona:
            return jsonify({'success': False, 'message': 'Persona no encontrada'}), 404
        
        nombre_persona = persona.nombre
        
        # Eliminar físicamente la persona y sus documentos asociados
        if persona.delete():
            return jsonify({
                'success': True, 
                'message': f'{nombre_persona} ha sido eliminada completamente del sistema'
            })
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar la persona'}), 500
            
    except Exception as e:
        logger.error(f"Error al eliminar persona: {e}")
        return jsonify({'success': False, 'message': f'Error al eliminar la persona: {str(e)}'}), 500

@personas_bp.route('/buscar')
@login_required
def buscar_personas():
    """Buscar personas responsables por nombre o cliente"""
    try:
        termino = request.args.get('q', '').strip()
        cliente_id = request.args.get('cliente_id')
        
        if not termino and not cliente_id:
            return jsonify({'personas': []})
        
        db = DatabaseManager()
        
        if cliente_id:
            # Buscar por cliente específico
            personas = db.execute_query(
                """SELECT * FROM personas_responsables 
                   WHERE cliente_id = ? AND activo = 1
                   ORDER BY es_principal DESC, nombre""",
                (cliente_id,)
            )
        else:
            # Buscar por término en nombre
            personas = db.execute_query(
                """SELECT pr.*, c.nombre as cliente_nombre 
                   FROM personas_responsables pr
                   JOIN clientes c ON pr.cliente_id = c.id
                   WHERE (pr.nombre LIKE ? OR c.nombre LIKE ?) AND pr.activo = 1
                   ORDER BY pr.es_principal DESC, pr.nombre""",
                (f'%{termino}%', f'%{termino}%')
            )
        
        return jsonify({'personas': personas})
        
    except Exception as e:
        logger.error(f"Error al buscar personas: {e}")
        return jsonify({'error': 'Error en la búsqueda'}), 500

@personas_bp.route('/por_cliente/<int:cliente_id>')
@login_required
def personas_por_cliente(cliente_id):
    """Obtener personas responsables de un cliente específico"""
    try:
        personas = PersonaResponsable.obtener_por_cliente(cliente_id)
        return jsonify({'personas': personas})
    except Exception as e:
        logger.error(f"Error al obtener personas por cliente: {e}")
        return jsonify({'error': 'Error al obtener personas'}), 500

@personas_bp.route('/api/search')
@login_required
def search_personas():
    """Buscar personas responsables por nombre, cargo o email"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'personas': []})
        
        personas = PersonaResponsable.search(search_term)
        
        # Convertir a diccionario para JSON
        personas_data = []
        for persona in personas:
            personas_data.append({
                'id': persona.id,
                'nombre': persona.nombre,
                'cargo': persona.cargo,
                'email': persona.email,
                'telefono': persona.telefono,
                'cliente_id': persona.cliente_id
            })
        
        return jsonify({'personas': personas_data})
    except Exception as e:
        logger.error(f"Error al buscar personas: {e}")
        return jsonify({'error': 'Error en la búsqueda'}), 500

@personas_bp.route('/api/get_by_ids', methods=['POST'])
@login_required
def get_personas_by_ids():
    """Obtener personas responsables por lista de IDs"""
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'success': False, 'error': 'IDs requeridos'}), 400
        
        ids = data['ids']
        if not isinstance(ids, list) or not ids:
            return jsonify({'success': False, 'error': 'Lista de IDs inválida'}), 400
        
        personas = PersonaResponsable.get_by_ids(ids)
        
        # Convertir a diccionario para JSON
        personas_data = []
        for persona in personas:
            personas_data.append({
                'id': persona.id,
                'nombre': persona.nombre,
                'cargo': persona.cargo,
                'email': persona.email,
                'telefono': persona.telefono,
                'cliente_id': persona.cliente_id
            })
        
        return jsonify({'success': True, 'personas': personas_data})
    except Exception as e:
        logger.error(f"Error al obtener personas por IDs: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener personas'}), 500

@personas_bp.route('/api/all')
@login_required
def get_all_personas():
    """API endpoint para obtener todas las personas responsables con información de clientes"""
    try:
        # Obtener todas las personas (incluyendo inactivas)
        personas = PersonaResponsable.get_all(activos_solo=False)
        
        # Obtener información de clientes
        clientes = {}
        for persona in personas:
            if persona.cliente_id and persona.cliente_id not in clientes:
                cliente = Cliente.get_by_id(persona.cliente_id)
                if cliente:
                    clientes[persona.cliente_id] = cliente
        
        # Formatear datos para el frontend
        personas_data = []
        for persona in personas:
            cliente = clientes.get(persona.cliente_id) if persona.cliente_id else None
            persona_dict = {
                'id': persona.id,
                'nombre': persona.nombre,
                'cliente_id': persona.cliente_id,
                'cliente_nombre': cliente.nombre if cliente else 'Sin cliente',
                'cargo': persona.cargo,
                'email': persona.email,
                'telefono': persona.telefono,
                'activo': persona.activo,
                'es_principal': persona.es_principal,
                'documento_path': persona.documento_path
            }
            personas_data.append(persona_dict)
        
        return jsonify({
            'success': True,
            'personas': personas_data
        })
        
    except Exception as e:
        logger.error(f"Error al obtener todas las personas: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener personas'}), 500