from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import Usuario, ActividadSistema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('login.html')
        
        # Buscar usuario en la base de datos
        usuario = Usuario.get_by_username(username)
        
        if usuario and usuario.verificar_password(password):
            # Login exitoso
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            session['nombre'] = usuario.nombre
            session['es_admin'] = usuario.es_admin
            
            # Registrar actividad
            actividad = ActividadSistema(
                usuario_id=usuario.id,
                accion='Inicio de Sesión',
                tabla_afectada='usuarios',
                registro_id=usuario.id,
                detalles=f'Usuario {usuario.username} inició sesión'
            )
            actividad.save()
            
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        # Registrar actividad de logout
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Cierre de Sesión',
            tabla_afectada='usuarios',
            registro_id=session['user_id'],
            detalles=f'Usuario {session.get("username", "")} cerró sesión'
        )
        actividad.save()
    
    session.clear()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('auth.login'))