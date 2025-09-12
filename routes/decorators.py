from flask import session, redirect, url_for, flash, jsonify
from functools import wraps
from database.models import Usuario


def login_required(f):
    """
    Decorador para requerir autenticación en rutas web.
    Redirige a la página de login si el usuario no está autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """
    Decorador para requerir autenticación en rutas API.
    Retorna JSON con error 401 si el usuario no está autenticado.
    """
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


def admin_required(f):
    """
    Decorador para requerir permisos de administrador.
    Verifica que el usuario esté autenticado y sea administrador.
    """
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


def api_admin_required(f):
    """
    Decorador para requerir permisos de administrador en rutas API.
    Retorna JSON con error si el usuario no es administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'message': 'No autenticado',
                'redirect': url_for('auth.login')
            }), 401
        
        usuario = Usuario.get_by_id(session['user_id'])
        if not usuario or not usuario.es_admin:
            return jsonify({
                'success': False,
                'message': 'Acceso denegado. Se requieren permisos de administrador.'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function