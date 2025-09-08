from flask import Blueprint, render_template, jsonify, request, flash, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from database.models import Usuario, ActividadSistema, Contrato, Notificacion
from services.system_metrics import get_system_metrics
from services.user_stats import get_user_personal_stats

users_bp = Blueprint('users', __name__)

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

@users_bp.route('/usuario')
@login_required
def usuario():
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Calcular días activos basado en fecha_creacion
    dias_activo = 0
    if usuario_actual and usuario_actual.fecha_creacion:
        try:
            if isinstance(usuario_actual.fecha_creacion, str):
                fecha_creacion = datetime.strptime(usuario_actual.fecha_creacion, '%Y-%m-%d %H:%M:%S')
            else:
                fecha_creacion = usuario_actual.fecha_creacion
            dias_activo = (datetime.now() - fecha_creacion).days
        except:
            dias_activo = 0
    
    # Determinar nivel de acceso dinámicamente
    nivel_acceso = 'Administrador' if usuario_actual and usuario_actual.es_admin else 'Usuario'
    
    # Añadir campos dinámicos al objeto usuario
    if usuario_actual:
        usuario_actual.dias_activo = dias_activo
        usuario_actual.nivel_acceso = nivel_acceso
    
    # Obtener estadísticas de contratos
    from .main import obtener_estadisticas_contratos
    estadisticas_contratos = obtener_estadisticas_contratos()
    
    # Calcular estadísticas del usuario
    from database.models import Contrato
    contratos = Contrato.get_all()
    contratos_usuario = [c for c in contratos if usuario_actual and c.usuario_responsable_id == usuario_actual.id]
    
    # Obtener reportes del mes actual
    import random
    reportes_mes = random.randint(15, 35)  # Simulado por ahora
    
    # Obtener actividades recientes del usuario
    actividades_db = ActividadSistema.get_recent(10)
    actividades_usuario = []
    
    for actividad in actividades_db:
        if actividad.usuario_id == usuario_actual.id if usuario_actual else False:
            actividades_usuario.append({
                'accion': actividad.accion,
                'fecha': actividad.fecha_actividad,
                'detalles': actividad.detalles
            })
    
    # Limitar a las últimas 5 actividades
    actividades_usuario = actividades_usuario[:5]
    
    # Estadísticas del usuario
    estadisticas_usuario = {
        'contratos_asignados': len(contratos_usuario),
        'contratos_activos': len([c for c in contratos_usuario if c.estado == 'activo']),
        'proximos_vencer': len([c for c in contratos_usuario if c.estado == 'activo']),  # Simulado
        'valor_total': '2.4M',  # Simulado
        'reportes_generados': reportes_mes,
        'actividades_recientes': len(actividades_usuario)
    }
    
    # Obtener métricas del sistema/servidor
    metricas_servidor = get_system_metrics()
    
    # Obtener estadísticas personales del usuario
    estadisticas_personales = get_user_personal_stats(usuario_actual.id if usuario_actual else 1)
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('usuario.html', 
                         usuario=usuario_actual,
                         estadisticas=estadisticas_usuario,
                         actividades=actividades_usuario,
                         metricas_servidor=metricas_servidor,
                         estadisticas_personales=estadisticas_personales,
                         notificaciones_count=notificaciones_count)

@users_bp.route('/usuarios_lista')
@admin_required
def usuarios_lista():
    """Página de lista de usuarios (solo para administradores)"""
    # Obtener todos los usuarios
    usuarios = Usuario.get_all()
    
    # Calcular estadísticas
    total_usuarios = len(usuarios)
    usuarios_activos = len([u for u in usuarios if u.activo])
    usuarios_inactivos = total_usuarios - usuarios_activos
    administradores = len([u for u in usuarios if u.es_admin])
    usuarios_regulares = total_usuarios - administradores
    
    estadisticas = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'administradores': administradores,
        'usuarios_regulares': usuarios_regulares
    }
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('usuarios_lista.html', 
                         usuarios=usuarios,
                         estadisticas=estadisticas,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count)

@users_bp.route('/crear_usuario', methods=['GET', 'POST'])
@admin_required
def crear_usuario():
    """Crear nuevo usuario (solo administradores)"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            telefono = request.form.get('telefono')
            cargo = request.form.get('cargo')
            departamento = request.form.get('departamento')
            es_admin = request.form.get('es_admin') == 'on'
            
            # Validaciones básicas
            if not all([nombre, email, username, password]):
                return jsonify({
                    'success': False,
                    'message': 'Todos los campos obligatorios deben ser completados'
                }), 400
            
            # Generar username único si ya existe
            original_username = username
            counter = 1
            while Usuario.get_by_username(username):
                username = f"{original_username}{counter}"
                counter += 1
                # Evitar bucle infinito
                if counter > 999:
                    return jsonify({
                        'success': False,
                        'message': 'No se pudo generar un nombre de usuario único'
                    }), 400
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                username=username,
                password=password,
                telefono=telefono,
                cargo=cargo,
                departamento=departamento,
                es_admin=es_admin
            )
            
            nuevo_usuario.save()
            
            # Registrar actividad
            actividad = ActividadSistema(
                usuario_id=session['user_id'],
                accion='Creación de Usuario',
                tabla_afectada='usuarios',
                registro_id=nuevo_usuario.id,
                detalles=f'Usuario {username} creado por {session.get("username", "")}'
            )
            actividad.save()
            
            return jsonify({
                'success': True,
                'message': f'Usuario {username} creado exitosamente'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al crear usuario: {str(e)}'
            }), 500
    
    # GET request - mostrar formulario
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('crear_usuario.html', 
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count)

# Ruta para editar perfil de usuario
@users_bp.route('/editar_perfil', methods=['POST'])
@api_login_required
def editar_perfil():
    """Permite a los usuarios editar su propio perfil"""
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        if not usuario_actual:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        cargo = request.form.get('cargo', '').strip()
        departamento = request.form.get('departamento', '').strip()
        password_actual = request.form.get('password_actual', '')
        nueva_password = request.form.get('nueva_password', '')
        confirmar_password = request.form.get('confirmar_password', '')
        
        # Validaciones básicas
        if not nombre:
            return jsonify({
                'success': False,
                'message': 'El nombre es obligatorio'
            }), 400
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'El email es obligatorio'
            }), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        # Si se quiere cambiar la contraseña
        if nueva_password:
            if not password_actual:
                return jsonify({
                    'success': False,
                    'message': 'Debe proporcionar la contraseña actual para cambiarla'
                }), 400
            
            if not usuario_actual.verificar_password(password_actual):
                return jsonify({
                    'success': False,
                    'message': 'La contraseña actual es incorrecta'
                }), 400
            
            if nueva_password != confirmar_password:
                return jsonify({
                    'success': False,
                    'message': 'Las contraseñas no coinciden'
                }), 400
            
            if len(nueva_password) < 6:
                return jsonify({
                    'success': False,
                    'message': 'La contraseña debe tener al menos 6 caracteres'
                }), 400
        
        # Actualizar datos del usuario
        usuario_actual.nombre = nombre
        usuario_actual.email = email
        usuario_actual.telefono = telefono
        usuario_actual.cargo = cargo
        usuario_actual.departamento = departamento
        
        # Actualizar contraseña si se proporcionó
        if nueva_password:
            usuario_actual.password = nueva_password
        
        # Guardar cambios
        usuario_actual.save()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Actualización de Perfil',
            tabla_afectada='usuarios',
            registro_id=usuario_actual.id,
            detalles=f'Usuario {usuario_actual.username} actualizó su perfil'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': 'Perfil actualizado exitosamente',
            'usuario': {
                'nombre': usuario_actual.nombre,
                'email': usuario_actual.email,
                'telefono': usuario_actual.telefono,
                'cargo': usuario_actual.cargo,
                'departamento': usuario_actual.departamento
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar perfil: {str(e)}'
        }), 500

# Ruta para editar usuario (solo admin)
@users_bp.route('/editar_usuario/<int:user_id>', methods=['POST'])
@api_login_required
@admin_required
def editar_usuario(user_id):
    """Permite a los administradores editar cualquier usuario, incluyendo roles"""
    try:
        # Obtener usuario a editar
        usuario_a_editar = Usuario.get_by_id(user_id)
        if not usuario_a_editar:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        cargo = request.form.get('cargo', '').strip()
        departamento = request.form.get('departamento', '').strip()
        es_admin = request.form.get('es_admin') == 'true'
        activo = request.form.get('activo', 'true') == 'true'
        nueva_password = request.form.get('nueva_password', '')
        
        # Validaciones básicas
        if not nombre:
            return jsonify({
                'success': False,
                'message': 'El nombre es obligatorio'
            }), 400
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'El email es obligatorio'
            }), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'message': 'Formato de email inválido'
            }), 400
        
        # Verificar que no se está quitando admin al último administrador
        if usuario_a_editar.es_admin and not es_admin:
            administradores = [u for u in Usuario.get_all() if u.es_admin and u.activo and u.id != user_id]
            if len(administradores) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No se puede quitar el rol de administrador al último administrador del sistema'
                }), 400
        
        # Actualizar datos del usuario
        usuario_a_editar.nombre = nombre
        usuario_a_editar.email = email
        usuario_a_editar.telefono = telefono
        usuario_a_editar.cargo = cargo
        usuario_a_editar.departamento = departamento
        usuario_a_editar.es_admin = es_admin
        usuario_a_editar.activo = activo
        
        # Actualizar contraseña si se proporcionó
        if nueva_password and len(nueva_password) >= 6:
            usuario_a_editar.password = nueva_password
        
        # Guardar cambios
        usuario_a_editar.save()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Edición de Usuario',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario {usuario_a_editar.username} editado por {session.get("username", "")}'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {usuario_a_editar.username} actualizado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al editar usuario: {str(e)}'
        }), 500

# Ruta para eliminar usuarios (solo admin)
@users_bp.route('/eliminar_usuario/<int:user_id>', methods=['DELETE'])
@api_login_required
@admin_required
def eliminar_usuario(user_id):
    """Eliminar usuario (solo administradores)"""
    try:
        # Verificar que el usuario existe
        usuario_a_eliminar = Usuario.get_by_id(user_id)
        if not usuario_a_eliminar:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Verificar que no se está intentando eliminar a sí mismo
        if user_id == session['user_id']:
            return jsonify({
                'success': False,
                'message': 'No puedes eliminar tu propia cuenta'
            }), 400
        
        # Verificar que no es el último administrador
        if usuario_a_eliminar.es_admin:
            administradores = [u for u in Usuario.get_all() if u.es_admin and u.activo]
            if len(administradores) <= 1:
                return jsonify({
                    'success': False,
                    'message': 'No se puede eliminar el último administrador del sistema'
                }), 400
        
        # Realizar eliminación lógica
        usuario_a_eliminar.delete()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Eliminación de Usuario',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario {usuario_a_eliminar.username} eliminado por {session.get("username", "")}'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {usuario_a_eliminar.username} eliminado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
                'success': False,
                'message': f'Error al eliminar usuario: {str(e)}'
            }), 500

# Ruta API para obtener datos de un usuario específico
@users_bp.route('/api/usuario/<int:user_id>', methods=['GET'])
@api_login_required
@admin_required
def obtener_usuario_api(user_id):
    """Obtiene los datos de un usuario específico (solo para administradores)"""
    try:
        usuario = Usuario.get_by_id(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'telefono': usuario.telefono,
                'cargo': usuario.cargo,
                'departamento': usuario.departamento,
                'es_admin': usuario.es_admin,
                'activo': usuario.activo,
                'fecha_creacion': usuario.fecha_creacion
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener usuario: {str(e)}'
        }), 500