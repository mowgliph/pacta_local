from flask import Blueprint, render_template, jsonify, request, flash, session, redirect, url_for
from datetime import datetime, timedelta
from database.models import Usuario, ActividadSistema, Contrato, Notificacion
from services.system_metrics import get_system_metrics
from services.user_stats import get_user_personal_stats
from .decorators import login_required, admin_required, api_login_required
from .utils import get_notificaciones_count, get_current_user_id, create_success_response, create_error_response

users_bp = Blueprint('users', __name__)

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
    # Obtener los últimos 10 usuarios agregados recientemente
    usuarios = Usuario.get_recent(limit=10, activos_solo=False)
    
    # Calcular estadísticas
    total_usuarios = len(usuarios)
    usuarios_activos = len([u for u in usuarios if u.activo])
    usuarios_inactivos = total_usuarios - usuarios_activos
    administradores = len([u for u in usuarios if u.es_admin])
    usuarios_regulares = len([u for u in usuarios if u.activo and getattr(u, 'rol', 'user') == 'user'])
    
    # Calcular usuarios invitados usando el campo rol
    usuarios_invitados = len([u for u in usuarios if u.activo and getattr(u, 'rol', 'user') == 'guest'])
    
    estadisticas = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'administradores': administradores,
        'usuarios_regulares': usuarios_regulares,
        'usuarios_invitados': usuarios_invitados
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
            rol = request.form.get('rol', 'user')
            es_admin = request.form.get('es_admin') == 'on' or rol == 'admin'
            
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
                es_admin=es_admin,
                rol=rol
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
        rol = request.form.get('rol', 'user')
        es_admin = request.form.get('es_admin') == 'true' or rol == 'admin'
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
        usuario_a_editar.rol = rol
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
        
        # Realizar eliminación física
        usuario_a_eliminar.delete()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Eliminación Física de Usuario',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario {usuario_a_eliminar.username} eliminado permanentemente por {session.get("username", "")}'
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

@users_bp.route('/api/usuario/<int:user_id>', methods=['PUT'])
@api_login_required
@admin_required
def update_user_api(user_id):
    """
    API para actualizar un usuario
    Solo accesible para administradores
    """
    try:
        # Obtener el usuario a actualizar
        usuario = Usuario.get_by_id(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Obtener datos del request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos para actualizar'
            }), 400
        
        # Validaciones
        if 'email' in data:
            # Verificar que el email no esté en uso por otro usuario
            usuarios = Usuario.get_all()
            existing_user = next((u for u in usuarios if u.email == data['email'] and u.id != user_id), None)
            
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'El email ya está en uso por otro usuario'
                }), 400
        
        if 'username' in data:
            # Verificar que el username no esté en uso por otro usuario
            existing_user = Usuario.get_by_username(data['username'])
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'success': False,
                    'message': 'El nombre de usuario ya está en uso'
                }), 400
        
        # Actualizar campos permitidos
        if 'nombre' in data:
            usuario.nombre = data['nombre'].strip()
        
        if 'email' in data:
            usuario.email = data['email'].strip().lower()
        
        if 'username' in data:
            usuario.username = data['username'].strip()
        
        if 'cargo' in data:
            usuario.cargo = data['cargo'].strip() if data['cargo'] else None
        
        if 'telefono' in data:
            usuario.telefono = data['telefono'].strip() if data['telefono'] else None
        
        if 'departamento' in data:
            usuario.departamento = data['departamento'].strip() if data['departamento'] else None
        
        if 'es_admin' in data:
            # Verificar que no se esté desactivando el último admin
            if not data['es_admin'] and usuario.es_admin:
                usuarios = Usuario.get_all()
                admin_count = len([u for u in usuarios if u.es_admin and u.activo])
                if admin_count <= 1:
                    return jsonify({
                        'success': False,
                        'message': 'No se puede quitar privilegios de administrador al último administrador activo'
                    }), 400
            
            usuario.es_admin = data['es_admin']
        
        if 'rol' in data:
            # Validar que el rol sea válido
            roles_validos = ['admin', 'user', 'guest']
            if data['rol'] not in roles_validos:
                return jsonify({
                    'success': False,
                    'message': f'Rol inválido. Los roles válidos son: {", ".join(roles_validos)}'
                }), 400
            
            usuario.rol = data['rol']
        
        if 'activo' in data:
            # No permitir desactivar al usuario actual
            if user_id == session['user_id'] and not data['activo']:
                return jsonify({
                    'success': False,
                    'message': 'No puedes desactivar tu propia cuenta'
                }), 400
            
            # Si se está desactivando un admin, verificar que no sea el último
            if usuario.es_admin and not data['activo']:
                usuarios = Usuario.get_all()
                administradores_activos = [u for u in usuarios if u.es_admin and u.activo and u.id != user_id]
                if len(administradores_activos) == 0:
                    return jsonify({
                        'success': False,
                        'message': 'No se puede desactivar al último administrador del sistema'
                    }), 400
            
            usuario.activo = data['activo']
        
        # Guardar cambios
        usuario.save()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Actualización de Usuario (API)',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario {usuario.username} actualizado por {session.get("username", "")}'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente',
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'username': usuario.username,
                'cargo': usuario.cargo,
                'telefono': usuario.telefono,
                'departamento': usuario.departamento,
                'es_admin': usuario.es_admin,
                'activo': usuario.activo
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
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
                'rol': usuario.rol,
                'activo': usuario.activo,
                'fecha_creacion': usuario.fecha_creacion
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener usuario: {str(e)}'
        }), 500

# Ruta para activar/desactivar usuarios (solo admin)
@users_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@api_login_required
@admin_required
def toggle_user_status(user_id):
    """Activar o desactivar usuario (solo administradores)"""
    try:
        # Obtener datos del request
        data = request.get_json()
        activate = data.get('activate', True)
        
        # Verificar que el usuario existe
        usuario = Usuario.get_by_id(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # No permitir desactivar al usuario actual
        if user_id == session['user_id'] and not activate:
            return jsonify({
                'success': False,
                'message': 'No puedes desactivar tu propia cuenta'
            }), 400
        
        # Si se está desactivando un admin, verificar que no sea el último
        if usuario.es_admin and not activate:
            administradores_activos = [u for u in Usuario.get_all() if u.es_admin and u.activo and u.id != user_id]
            if len(administradores_activos) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No se puede desactivar al último administrador del sistema'
                }), 400
        
        # Actualizar estado del usuario
        usuario.activo = activate
        usuario.save()
        
        # Registrar actividad
        accion = 'Activación' if activate else 'Desactivación'
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion=f'{accion} de Usuario',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario {usuario.username} {"activado" if activate else "desactivado"} por {session.get("username", "")}'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {"activado" if activate else "desactivado"} exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cambiar estado del usuario: {str(e)}'
        }), 500

@users_bp.route('/api/usuario/<int:user_id>', methods=['DELETE'])
@api_login_required
@admin_required
def delete_user_api(user_id):
    """Eliminar un usuario específico"""
    try:
        # Obtener el usuario a eliminar
        user_to_delete = Usuario.get_by_id(user_id)
        if not user_to_delete:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Verificar que no sea el último administrador
        if user_to_delete.es_admin:
            administradores_activos = [u for u in Usuario.get_all() if u.es_admin and u.activo and u.id != user_id]
            if len(administradores_activos) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No se puede eliminar el último administrador del sistema'
                }), 400
        
        # Verificar que no se esté eliminando a sí mismo
        if user_to_delete.id == session['user_id']:
            return jsonify({
                'success': False,
                'message': 'No puedes eliminar tu propia cuenta'
            }), 400
        
        # Guardar información para el log
        deleted_username = user_to_delete.username
        deleted_email = user_to_delete.email
        
        # Eliminar el usuario (eliminación física)
        user_to_delete.delete()
        
        # Registrar la actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Eliminación Física de Usuario (API)',
            tabla_afectada='usuarios',
            registro_id=user_id,
            detalles=f'Usuario eliminado permanentemente: {deleted_username} ({deleted_email}) por {session.get("username", "")}'
        )
        actividad.save()
        
        return jsonify({
            'success': True,
            'message': f'Usuario {deleted_username} eliminado correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500