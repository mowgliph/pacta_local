from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from database.models import PersonaResponsable, Cliente, Notificacion
from database.database import DatabaseManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para personas responsables
personas_bp = Blueprint('personas', __name__, url_prefix='/personas')

# Función helper para obtener contador de notificaciones
def get_notificaciones_count():
    """Obtiene el número de notificaciones no leídas del usuario actual"""
    if 'user_id' in session:
        return Notificacion.get_unread_count(session['user_id'])
    return 0

# Decorador para requerir login (simplificado)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Aquí iría la lógica de verificación de sesión
        # Por ahora permitimos el acceso
        return f(*args, **kwargs)
    return decorated_function

@personas_bp.route('/')
@login_required
def listar_personas():
    """Mostrar lista de todas las personas responsables"""
    try:
        # Obtener todas las personas responsables
        personas = PersonaResponsable.obtener_todos()
        
        # Obtener información de clientes para mostrar nombres
        clientes = {}
        for persona in personas:
            if persona['cliente_id'] not in clientes:
                cliente = Cliente.obtener_por_id(persona['cliente_id'])
                if cliente:
                    clientes[persona['cliente_id']] = cliente
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('personas/listar.html', 
                             personas=personas, 
                             clientes=clientes,
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
            cliente_id = request.form.get('cliente_id')
            nombre = request.form.get('nombre')
            cargo = request.form.get('cargo')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            es_principal = request.form.get('es_principal') == 'on'
            
            # Validar datos requeridos
            if not cliente_id or not nombre:
                flash('Cliente y nombre son campos obligatorios', 'error')
                return redirect(request.url)
            
            # Si es principal, desactivar otros principales del mismo cliente
            if es_principal:
                db = DatabaseManager()
                db.execute_query(
                    "UPDATE personas_responsables SET es_principal = 0 WHERE cliente_id = ?",
                    (cliente_id,)
                )
            
            # Crear nueva persona
            persona = PersonaResponsable(
                cliente_id=int(cliente_id),
                nombre=nombre,
                cargo=cargo,
                telefono=telefono,
                email=email,
                es_principal=es_principal
            )
            
            persona_id = persona.guardar()
            
            if persona_id:
                flash('Persona responsable creada exitosamente', 'success')
                return redirect(url_for('personas.listar_personas'))
            else:
                flash('Error al crear la persona responsable', 'error')
                
        except Exception as e:
            logger.error(f"Error al crear persona: {e}")
            flash('Error al crear la persona responsable', 'error')
    
    # Obtener lista de clientes para el formulario
    try:
        clientes = Cliente.obtener_todos()
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
        persona = PersonaResponsable.obtener_por_id(persona_id)
        if not persona:
            flash('Persona no encontrada', 'error')
            return redirect(url_for('personas.listar_personas'))
        
        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            cargo = request.form.get('cargo')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            es_principal = request.form.get('es_principal') == 'on'
            activo = request.form.get('activo') == 'on'
            
            # Validar datos requeridos
            if not nombre:
                flash('El nombre es obligatorio', 'error')
                return redirect(request.url)
            
            # Si es principal, desactivar otros principales del mismo cliente
            if es_principal and not persona['es_principal']:
                db = DatabaseManager()
                db.execute_query(
                    "UPDATE personas_responsables SET es_principal = 0 WHERE cliente_id = ? AND id != ?",
                    (persona['cliente_id'], persona_id)
                )
            
            # Actualizar persona
            db = DatabaseManager()
            resultado = db.execute_update(
                """UPDATE personas_responsables 
                   SET nombre = ?, cargo = ?, telefono = ?, email = ?, 
                       es_principal = ?, activo = ?
                   WHERE id = ?""",
                (nombre, cargo, telefono, email, es_principal, activo, persona_id)
            )
            
            if resultado:
                flash('Persona actualizada exitosamente', 'success')
                return redirect(url_for('personas.listar_personas'))
            else:
                flash('Error al actualizar la persona', 'error')
        
        # Obtener lista de clientes para el formulario
        clientes = Cliente.obtener_todos()
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        return render_template('personas/editar.html', persona=persona, clientes=clientes, notificaciones_count=notificaciones_count)
        
    except Exception as e:
        logger.error(f"Error al editar persona: {e}")
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('personas.listar_personas'))

@personas_bp.route('/eliminar/<int:persona_id>', methods=['POST'])
@login_required
def eliminar_persona(persona_id):
    """Eliminar persona responsable"""
    try:
        persona = PersonaResponsable.obtener_por_id(persona_id)
        if not persona:
            flash('Persona no encontrada', 'error')
            return redirect(url_for('personas.listar_personas'))
        
        # Marcar como inactivo en lugar de eliminar físicamente
        db = DatabaseManager()
        resultado = db.execute_update(
            "UPDATE personas_responsables SET activo = 0 WHERE id = ?",
            (persona_id,)
        )
        
        if resultado:
            flash('Persona eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la persona', 'error')
            
    except Exception as e:
        logger.error(f"Error al eliminar persona: {e}")
        flash('Error al eliminar la persona', 'error')
    
    return redirect(url_for('personas.listar_personas'))

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