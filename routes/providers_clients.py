from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify, request
from functools import wraps
from datetime import datetime, timedelta
from database.models import Usuario, Cliente, Contrato, Notificacion

providers_clients_bp = Blueprint('providers_clients', __name__)

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

# Decorador para requerir admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        usuario = Usuario.get_by_id(session['user_id'])
        if not usuario or not usuario.es_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para rutas API que requieren login
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'message': 'No autenticado',
                'redirect': url_for('auth.login')
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# ===== RUTAS DE PROVEEDORES =====

@providers_clients_bp.route('/proveedores')
@login_required
def proveedores():
    """Página de gestión de proveedores"""
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener todos los proveedores
        clientes = Cliente.get_all()
        proveedores = [c for c in clientes if c.tipo_cliente == 'proveedor']
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Calcular estadísticas de proveedores
        total_proveedores = len(proveedores)
        proveedores_activos = len([p for p in proveedores if p.activo])
        contratos_proveedores = [c for c in contratos if any(p.id == c.cliente_id for p in proveedores)]
        valor_total_proveedores = sum([c.monto_actual for c in contratos_proveedores if c.estado == 'activo'])
        
        estadisticas = {
            'total_proveedores': total_proveedores,
            'proveedores_activos': proveedores_activos,
            'contratos_totales': len(contratos_proveedores),
            'valor_promedio': int(valor_total_proveedores / len(contratos_proveedores)) if contratos_proveedores else 0
        }
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('proveedores.html', 
                             proveedores=proveedores,
                             estadisticas=estadisticas,
                             usuario=usuario_actual,
                             notificaciones_count=notificaciones_count)
    except Exception as e:
        flash(f'Error al cargar proveedores: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

# ===== RUTAS DE CLIENTES =====

@providers_clients_bp.route('/clientes')
@login_required
def clientes():
    """Página de gestión de clientes"""
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener todos los clientes
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Calcular estadísticas de clientes
        total_clientes = len(clientes)
        clientes_activos = len([c for c in clientes if c.activo])
        contratos_clientes = [c for c in contratos if any(cl.id == c.cliente_id for cl in clientes)]
        valor_total_clientes = sum([c.monto_actual for c in contratos_clientes if c.estado == 'activo'])
        
        estadisticas = {
            'total_clientes': total_clientes,
            'clientes_activos': clientes_activos,
            'contratos_totales': len(contratos_clientes),
            'valor_promedio': int(valor_total_clientes / len(contratos_clientes)) if contratos_clientes else 0
        }
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('clientes.html', 
                             clientes=clientes,
                             estadisticas=estadisticas,
                             usuario=usuario_actual,
                             notificaciones_count=notificaciones_count)
    except Exception as e:
        flash(f'Error al cargar clientes: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

# ===== RUTAS API PARA PROVEEDORES =====

@providers_clients_bp.route('/api/proveedores', methods=['GET'])
@api_login_required
def api_get_proveedores():
    """API para obtener lista de proveedores"""
    try:
        clientes = Cliente.get_all()
        proveedores = [c for c in clientes if c.tipo_cliente == 'proveedor']
        
        proveedores_data = []
        for proveedor in proveedores:
            proveedores_data.append({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'rfc': proveedor.rfc,
                'email': proveedor.email,
                'telefono': proveedor.telefono,
                'direccion': proveedor.direccion,
                'contacto_principal': proveedor.contacto_principal,
                'activo': proveedor.activo,
                'fecha_creacion': proveedor.fecha_creacion.isoformat() if proveedor.fecha_creacion else None
            })
        
        return jsonify({
            'success': True,
            'proveedores': proveedores_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener proveedores: {str(e)}'
        }), 500

@providers_clients_bp.route('/api/proveedores', methods=['POST'])
@api_login_required
def api_create_proveedor():
    """API para crear un nuevo proveedor"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'El nombre es requerido'
            }), 400
        
        # Crear nuevo proveedor
        proveedor = Cliente(
            nombre=data.get('nombre'),
            tipo_cliente='proveedor',
            rfc=data.get('rfc', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            contacto_principal=data.get('contacto_principal', ''),
            activo=data.get('activo', True)
        )
        
        proveedor.save()
        
        return jsonify({
            'success': True,
            'message': 'Proveedor creado exitosamente',
            'proveedor_id': proveedor.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear proveedor: {str(e)}'
        }), 500

# ===== RUTAS API PARA CLIENTES =====

@providers_clients_bp.route('/api/clientes', methods=['GET'])
@api_login_required
def api_get_clientes():
    """API para obtener lista de clientes"""
    try:
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        clientes_data = []
        for cliente in clientes:
            clientes_data.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'rfc': cliente.rfc,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'direccion': cliente.direccion,
                'contacto_principal': cliente.contacto_principal,
                'activo': cliente.activo,
                'fecha_creacion': cliente.fecha_creacion.isoformat() if cliente.fecha_creacion else None
            })
        
        return jsonify({
            'success': True,
            'clientes': clientes_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener clientes: {str(e)}'
        }), 500

@providers_clients_bp.route('/api/clientes', methods=['POST'])
@api_login_required
def api_create_cliente():
    """API para crear un nuevo cliente"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'El nombre es requerido'
            }), 400
        
        # Crear nuevo cliente
        cliente = Cliente(
            nombre=data.get('nombre'),
            tipo_cliente='cliente',
            rfc=data.get('rfc', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            contacto_principal=data.get('contacto_principal', ''),
            activo=data.get('activo', True)
        )
        
        cliente.save()
        
        return jsonify({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'cliente_id': cliente.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear cliente: {str(e)}'
        }), 500

# ===== RUTAS API PARA EDITAR Y ELIMINAR =====

@providers_clients_bp.route('/api/proveedores/<int:proveedor_id>', methods=['PUT'])
@api_login_required
def api_update_proveedor(proveedor_id):
    """API para actualizar un proveedor"""
    try:
        data = request.get_json()
        proveedor = Cliente.get_by_id(proveedor_id)
        
        if not proveedor or proveedor.tipo_cliente != 'proveedor':
            return jsonify({
                'success': False,
                'message': 'Proveedor no encontrado'
            }), 404
        
        # Actualizar campos
        if 'nombre' in data:
            proveedor.nombre = data['nombre']
        if 'rfc' in data:
            proveedor.rfc = data['rfc']
        if 'email' in data:
            proveedor.email = data['email']
        if 'telefono' in data:
            proveedor.telefono = data['telefono']
        if 'direccion' in data:
            proveedor.direccion = data['direccion']
        if 'contacto_principal' in data:
            proveedor.contacto_principal = data['contacto_principal']
        if 'activo' in data:
            proveedor.activo = data['activo']
        
        proveedor.save()
        
        return jsonify({
            'success': True,
            'message': 'Proveedor actualizado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar proveedor: {str(e)}'
        }), 500

@providers_clients_bp.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
@api_login_required
def api_update_cliente(cliente_id):
    """API para actualizar un cliente"""
    try:
        data = request.get_json()
        cliente = Cliente.get_by_id(cliente_id)
        
        if not cliente or cliente.tipo_cliente != 'cliente':
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado'
            }), 404
        
        # Actualizar campos
        if 'nombre' in data:
            cliente.nombre = data['nombre']
        if 'rfc' in data:
            cliente.rfc = data['rfc']
        if 'email' in data:
            cliente.email = data['email']
        if 'telefono' in data:
            cliente.telefono = data['telefono']
        if 'direccion' in data:
            cliente.direccion = data['direccion']
        if 'contacto_principal' in data:
            cliente.contacto_principal = data['contacto_principal']
        if 'activo' in data:
            cliente.activo = data['activo']
        
        cliente.save()
        
        return jsonify({
            'success': True,
            'message': 'Cliente actualizado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar cliente: {str(e)}'
        }), 500

@providers_clients_bp.route('/api/proveedores/<int:proveedor_id>', methods=['DELETE'])
@api_login_required
def api_delete_proveedor(proveedor_id):
    """API para eliminar un proveedor"""
    try:
        proveedor = Cliente.get_by_id(proveedor_id)
        
        if not proveedor or proveedor.tipo_cliente != 'proveedor':
            return jsonify({
                'success': False,
                'message': 'Proveedor no encontrado'
            }), 404
        
        # Verificar si tiene contratos asociados
        contratos = Contrato.get_all()
        contratos_proveedor = [c for c in contratos if c.cliente_id == proveedor_id]
        
        if contratos_proveedor:
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar el proveedor porque tiene contratos asociados'
            }), 400
        
        proveedor.delete()
        
        return jsonify({
            'success': True,
            'message': 'Proveedor eliminado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar proveedor: {str(e)}'
        }), 500

@providers_clients_bp.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
@api_login_required
def api_delete_cliente(cliente_id):
    """API para eliminar un cliente"""
    try:
        cliente = Cliente.get_by_id(cliente_id)
        
        if not cliente or cliente.tipo_cliente != 'cliente':
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado'
            }), 404
        
        # Verificar si tiene contratos asociados
        contratos = Contrato.get_all()
        contratos_cliente = [c for c in contratos if c.cliente_id == cliente_id]
        
        if contratos_cliente:
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar el cliente porque tiene contratos asociados'
            }), 400
        
        cliente.delete()
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar cliente: {str(e)}'
        }), 500