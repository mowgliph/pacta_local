from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import random
from functools import wraps
from database import db_manager
from database.models import Usuario, Cliente, Contrato, Suplemento, ActividadSistema, Notificacion
from services.contract_reminders import ContractReminderSystem

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración para desarrollo
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
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
                'redirect': url_for('login')
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.get_by_id(session['user_id'])
        if not usuario or not usuario.es_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Inicializa la base de datos y crea datos de ejemplo si no existen"""
    db_manager.init_database()
    
    # Verificar si ya existen usuarios
    usuarios = Usuario.get_all()
    if not usuarios:
        crear_datos_ejemplo()

# Inicializar la base de datos al arrancar la aplicación
with app.app_context():
    init_db()

def crear_datos_ejemplo():
    """Crea datos de ejemplo en la base de datos"""
    # Crear usuario administrador por defecto
    admin = Usuario(
        nombre='Administrador',
        email='admin@empresa.com',
        username='admin',
        password='admin123',
        cargo='Administrador del Sistema',
        departamento='TI',
        es_admin=True
    )
    admin.save()
    
    # Crear usuarios de ejemplo
    usuarios_ejemplo = [
        Usuario(nombre='Juan Pérez', email='juan.perez@empresa.com', username='juan.perez', password='123456', cargo='Gerente de Contratos', departamento='Legal'),
        Usuario(nombre='María García', email='maria.garcia@empresa.com', username='maria.garcia', password='123456', cargo='Analista de Contratos', departamento='Compras'),
        Usuario(nombre='Carlos López', email='carlos.lopez@empresa.com', username='carlos.lopez', password='123456', cargo='Director de Operaciones', departamento='Operaciones')
    ]
    
    for usuario in usuarios_ejemplo:
        usuario.save()
    
    # Crear clientes y proveedores de ejemplo
    clientes_ejemplo = [
        Cliente(nombre='Empresa ABC S.A.', tipo_cliente='cliente', rfc='ABC123456789', direccion='Av. Principal 123', telefono='555-0001', email='contacto@abc.com', contacto_principal='Ana Martínez'),
        Cliente(nombre='Corporativo XYZ', tipo_cliente='cliente', rfc='XYZ987654321', direccion='Calle Secundaria 456', telefono='555-0002', email='info@xyz.com', contacto_principal='Roberto Silva'),
        Cliente(nombre='Proveedor Tech Solutions', tipo_cliente='proveedor', rfc='TEC456789123', direccion='Zona Industrial 789', telefono='555-0003', email='ventas@techsol.com', contacto_principal='Laura Rodríguez'),
        Cliente(nombre='Servicios Integrales SA', tipo_cliente='proveedor', rfc='SIN789123456', direccion='Centro Comercial 321', telefono='555-0004', email='servicios@integrales.com', contacto_principal='Miguel Torres')
    ]
    
    for cliente in clientes_ejemplo:
        cliente.save()
    
    # Crear contratos de ejemplo
    tipos_contrato = ['Servicios', 'Suministro', 'Mantenimiento', 'Consultoría', 'Arrendamiento']
    estados = ['activo', 'borrador', 'suspendido', 'terminado']
    
    for i in range(1, 21):  # 20 contratos de ejemplo
        fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 365))
        duracion = random.randint(90, 730)  # Entre 3 meses y 2 años
        fecha_fin = fecha_inicio + timedelta(days=duracion)
        
        contrato = Contrato(
            numero_contrato=f'CONT-{i:03d}',
            cliente_id=random.randint(1, 4),  # IDs de los clientes creados
            usuario_responsable_id=random.randint(1, 3),  # IDs de los usuarios creados
            titulo=f'Contrato de {tipos_contrato[random.randint(0, len(tipos_contrato)-1)]} {i}',
            descripcion=f'Descripción detallada del contrato número {i}',
            monto_original=random.randint(50000, 1000000),
            monto_actual=random.randint(50000, 1000000),
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            estado=estados[random.randint(0, len(estados)-1)],
            tipo_contrato=tipos_contrato[random.randint(0, len(tipos_contrato)-1)]
        )
        contrato.save()
        
        # Crear algunos suplementos para algunos contratos
        if random.random() < 0.3:  # 30% de probabilidad de tener suplementos
            suplemento = Suplemento(
                contrato_id=contrato.id,
                numero_suplemento=f'SUP-{contrato.id}-001',
                tipo_modificacion='Ampliación de monto',
                descripcion=f'Suplemento para ampliación del contrato {contrato.numero_contrato}',
                monto_modificacion=random.randint(10000, 100000),
                fecha_modificacion=datetime.now().date(),
                usuario_autoriza_id=random.randint(1, 3),
                estado='aprobado'
            )
            suplemento.save()
    
    # Registrar actividad inicial
    actividad = ActividadSistema(
        usuario_id=1,
        accion='Inicialización del sistema',
        tabla_afectada='sistema',
        detalles='Creación de datos de ejemplo iniciales'
    )
    actividad.save()

def obtener_estadisticas_contratos():
    """Obtiene estadísticas de contratos desde la base de datos"""
    contratos = Contrato.get_all()
    
    total_contratos = len(contratos)
    contratos_activos = len([c for c in contratos if c.estado == 'activo'])
    
    # Calcular valor total
    valor_total = sum([c.monto_actual for c in contratos if c.estado == 'activo'])
    
    # Contratos próximos a vencer (30 días)
    fecha_limite = datetime.now().date() + timedelta(days=30)
    proximos_vencer = 0
    
    for c in contratos:
        if c.estado == 'activo' and c.fecha_fin:
            # Convertir fecha_fin de string a date si es necesario
            if isinstance(c.fecha_fin, str):
                try:
                    fecha_fin = datetime.strptime(c.fecha_fin, '%Y-%m-%d').date()
                except ValueError:
                    continue
            else:
                fecha_fin = c.fecha_fin
            
            if fecha_fin <= fecha_limite:
                proximos_vencer += 1
    
    return {
        'total_contratos': total_contratos,
        'contratos_activos': contratos_activos,
        'valor_total': valor_total,
        'proximos_vencer': proximos_vencer
    }

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
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
    return redirect(url_for('login'))

# Ruta principal - Redirigir a dashboard
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Ruta del Dashboard Principal
@app.route('/dashboard')
@login_required
def dashboard():
    # Obtener estadísticas reales de la base de datos
    estadisticas = obtener_estadisticas_contratos()
    
    # Obtener contratos recientes (últimos 5)
    contratos = Contrato.get_all()
    contratos_recientes = []
    for contrato in contratos[:5]:
        cliente = Cliente.get_by_id(contrato.cliente_id)
        usuario = Usuario.get_by_id(contrato.usuario_responsable_id)
        contratos_recientes.append({
            'id': contrato.numero_contrato,
            'nombre': contrato.titulo,
            'tipo': contrato.tipo_contrato,
            'proveedor': cliente.nombre if cliente else 'N/A',
            'fecha_inicio': contrato.fecha_inicio,
            'fecha_vencimiento': contrato.fecha_fin,
            'valor': contrato.monto_actual,
            'estado': contrato.estado.title(),
            'responsable': usuario.nombre if usuario else 'N/A'
        })
    
    # Obtener actividad reciente
    actividades = ActividadSistema.get_recent(5)
    actividad_reciente = []
    for actividad in actividades:
        usuario = Usuario.get_by_id(actividad.usuario_id) if actividad.usuario_id else None
        actividad_reciente.append({
            'usuario': usuario.nombre if usuario else 'Sistema',
            'accion': actividad.accion,
            'tiempo': actividad.fecha_actividad,
            'detalles': actividad.detalles
        })
    
    # Métricas adicionales simuladas
    total_reportes = 89
    reportes_mes = 23
    reportes_pendientes = 5
    usuarios_activos = 12
    sesiones_mes = 156
    uptime = 99.8
    tiempo_respuesta = 245  # ms
    
    estadisticas_completas = {
        'total_contratos': estadisticas['total_contratos'],
        'contratos_activos': estadisticas['contratos_activos'],
        'contratos_por_vencer': estadisticas['proximos_vencer'],
        'valor_total': f'{estadisticas["valor_total"]/1000000:.1f}M',
        'total_reportes': total_reportes,
        'reportes_mes': reportes_mes,
        'reportes_pendientes': reportes_pendientes,
        'usuarios_activos': usuarios_activos,
        'sesiones_mes': sesiones_mes,
        'uptime': uptime,
        'tiempo_respuesta': tiempo_respuesta
    }
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('dashboard.html', 
                         estadisticas=estadisticas_completas, 
                         contratos=contratos_recientes,
                         usuario=usuario_actual)

@app.route('/contratos')
@login_required
def contratos():
    # Obtener contratos reales de la base de datos
    contratos_db = Contrato.get_all()
    contratos_data = []
    
    for contrato in contratos_db:
        cliente = Cliente.get_by_id(contrato.cliente_id)
        usuario = Usuario.get_by_id(contrato.usuario_responsable_id)
        
        # Convertir fechas de string a date si es necesario
        if isinstance(contrato.fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(contrato.fecha_inicio, '%Y-%m-%d').date()
            except ValueError:
                fecha_inicio = datetime.now().date()
        else:
            fecha_inicio = contrato.fecha_inicio
            
        if isinstance(contrato.fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(contrato.fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                fecha_fin = datetime.now().date()
        else:
            fecha_fin = contrato.fecha_fin
        
        # Calcular días para vencer
        dias_para_vencer = (fecha_fin - datetime.now().date()).days
        
        contratos_data.append({
            'id': contrato.numero_contrato,
            'nombre': contrato.titulo,
            'tipo': contrato.tipo_contrato,
            'proveedor': cliente.nombre if cliente else 'N/A',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_vencimiento': fecha_fin.strftime('%Y-%m-%d'),
            'valor': contrato.monto_actual,
            'estado': contrato.estado.title(),
            'dias_para_vencer': dias_para_vencer,
            'responsable': usuario.nombre if usuario else 'N/A',
            'descripcion': contrato.descripcion
        })
    
    # Estadísticas para la página de contratos
    estadisticas = obtener_estadisticas_contratos()
    estadisticas['valor_total'] = f'{estadisticas["valor_total"]/1000000:.1f}M'
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('contratos.html', 
                         contratos=contratos_data, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual)

def obtener_todos_suplementos():
    """Obtiene todos los suplementos con información enriquecida"""
    suplementos = Suplemento.get_all()
    
    for suplemento in suplementos:
        # Enriquecer con información del contrato
        contrato = Contrato.get_by_id(suplemento.contrato_id)
        suplemento.contrato_numero = contrato.numero_contrato if contrato else 'N/A'
        suplemento.contrato_titulo = contrato.titulo if contrato else 'N/A'
        
        # Enriquecer con información del usuario
        usuario = Usuario.get_by_id(suplemento.usuario_autoriza_id)
        suplemento.usuario_autoriza_nombre = usuario.nombre if usuario else 'N/A'
    
    return suplementos

def obtener_estadisticas_suplementos():
    """Obtiene estadísticas de suplementos"""
    suplementos = Suplemento.get_all()
    
    total_suplementos = len(suplementos)
    suplementos_aprobados = len([s for s in suplementos if s.estado == 'aprobado'])
    suplementos_pendientes = len([s for s in suplementos if s.estado == 'pendiente'])
    suplementos_rechazados = len([s for s in suplementos if s.estado == 'rechazado'])
    
    # Calcular porcentajes
    porcentaje_aprobados = round((suplementos_aprobados / total_suplementos * 100) if total_suplementos > 0 else 0, 1)
    porcentaje_pendientes = round((suplementos_pendientes / total_suplementos * 100) if total_suplementos > 0 else 0, 1)
    
    # Calcular valor total de modificaciones
    valor_total_modificaciones = sum([s.monto_modificacion for s in suplementos if s.estado == 'aprobado'])
    
    # Estadísticas por tipo de modificación
    ampliacion_monto = len([s for s in suplementos if 'monto' in s.tipo_modificacion.lower()])
    extension_plazo = len([s for s in suplementos if 'plazo' in s.tipo_modificacion.lower()])
    modificacion_alcance = len([s for s in suplementos if 'alcance' in s.tipo_modificacion.lower()])
    otros_tipos = total_suplementos - ampliacion_monto - extension_plazo - modificacion_alcance
    
    return {
        'total_suplementos': total_suplementos,
        'suplementos_aprobados': suplementos_aprobados,
        'suplementos_pendientes': suplementos_pendientes,
        'suplementos_rechazados': suplementos_rechazados,
        'porcentaje_aprobados': porcentaje_aprobados,
        'porcentaje_pendientes': porcentaje_pendientes,
        'valor_total_modificaciones': valor_total_modificaciones,
        'ampliacion_monto': ampliacion_monto,
        'extension_plazo': extension_plazo,
        'modificacion_alcance': modificacion_alcance,
        'otros_tipos': otros_tipos
    }

@app.route('/suplementos')
@login_required
def suplementos():
    """Página de gestión de suplementos"""
    # Obtener todos los suplementos
    suplementos = obtener_todos_suplementos()
    
    # Obtener estadísticas
    estadisticas = obtener_estadisticas_suplementos()
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('suplementos.html', 
                         suplementos=suplementos, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual)

@app.route('/reportes')
@login_required
def reportes():
    # Datos simulados para reportes
    reportes_data = [
        {
            'id': 'RPT-001',
            'nombre': 'Análisis Financiero Q1',
            'tipo': 'Financiero',
            'fecha_generacion': '28/01/2025',
            'tamaño': '2.4 MB',
            'estado': 'Completado',
            'descargas': 45
        },
        {
            'id': 'RPT-002',
            'nombre': 'Reporte de Personal',
            'tipo': 'RRHH',
            'fecha_generacion': '25/01/2025',
            'tamaño': '1.8 MB',
            'estado': 'Completado',
            'descargas': 23
        },
        {
            'id': 'RPT-003',
            'nombre': 'Estado de Contratos',
            'tipo': 'Contratos',
            'fecha_generacion': '22/01/2025',
            'tamaño': '3.1 MB',
            'estado': 'Procesando',
            'descargas': 12
        }
    ]
    
    # Calcular estadísticas para la página de reportes
    estadisticas = {
        'reportes_generados': 89,
        'reportes_automaticos': 34,
        'tiempo_promedio': '2.3h',
        'descargas': 267
    }
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('reportes.html', 
                         reportes=reportes_data, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual)

@app.route('/configuracion')
@admin_required
def configuracion():
    # Generar estadísticas para la página de configuración
    estadisticas = {
        'usuarios_activos': 24,
        'configuraciones': 12,
        'ultimo_backup': 'Ayer',
        'espacio_usado': '68%'
    }
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('configuracion.html', 
                         estadisticas=estadisticas,
                         usuario=usuario_actual)

@app.route('/usuario')
@login_required
def usuario():
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Obtener estadísticas de contratos
    estadisticas_contratos = obtener_estadisticas_contratos()
    
    # Calcular estadísticas del usuario
    contratos = Contrato.get_all()
    contratos_usuario = [c for c in contratos if usuario_actual and c.usuario_responsable_id == usuario_actual.id]
    
    # Obtener reportes del mes actual
    reportes_mes = random.randint(15, 35)  # Simulado por ahora
    
    # Obtener actividades recientes del usuario
    actividades_db = ActividadSistema.get_recent(10)
    actividades_usuario = []
    
    for actividad in actividades_db:
        if actividad.usuario_id == usuario_actual.id if usuario_actual else False:
            # Determinar el icono y color basado en la acción
            if 'contrato' in actividad.accion.lower():
                if 'creó' in actividad.accion.lower() or 'nuevo' in actividad.accion.lower():
                    icono = 'fas fa-file-plus'
                    color = '#10b981'
                elif 'actualizó' in actividad.accion.lower() or 'modificó' in actividad.accion.lower():
                    icono = 'fas fa-edit'
                    color = '#f59e0b'
                elif 'renovó' in actividad.accion.lower():
                    icono = 'fas fa-redo'
                    color = '#3b82f6'
                else:
                    icono = 'fas fa-file-contract'
                    color = '#6b7280'
            elif 'reporte' in actividad.accion.lower():
                icono = 'fas fa-chart-line'
                color = '#3b82f6'
            elif 'suplemento' in actividad.accion.lower():
                icono = 'fas fa-plus-circle'
                color = '#8b5cf6'
            elif 'configuración' in actividad.accion.lower() or 'sistema' in actividad.accion.lower():
                icono = 'fas fa-cog'
                color = '#8b5cf6'
            else:
                icono = 'fas fa-info-circle'
                color = '#6b7280'
            
            # Determinar el estado basado en la acción
            if 'completado' in actividad.detalles.lower() or 'creó' in actividad.accion.lower() or 'generó' in actividad.accion.lower():
                estado = 'Completado'
                estado_clase = 'status-success'
            elif 'revisión' in actividad.detalles.lower() or 'actualizó' in actividad.accion.lower():
                estado = 'En Revisión'
                estado_clase = 'status-warning'
            elif 'procesando' in actividad.detalles.lower():
                estado = 'Procesando'
                estado_clase = 'status-processing'
            else:
                estado = 'Registrado'
                estado_clase = 'status-info'
            
            actividades_usuario.append({
                'accion': actividad.accion,
                'descripcion': actividad.detalles or f'Actividad: {actividad.accion}',
                'fecha': actividad.fecha_actividad,
                'estado': estado,
                'estado_clase': estado_clase,
                'icono': icono,
                'color': color
            })
    
    # Si no hay suficientes actividades del usuario, agregar algunas de ejemplo
    if len(actividades_usuario) < 5:
        actividades_ejemplo = [
            {
                'accion': 'Perfil Actualizado',
                'descripcion': 'Información de perfil actualizada',
                'fecha': '2024-02-15 10:30:00',
                'estado': 'Completado',
                'estado_clase': 'status-success',
                'icono': 'fas fa-user-edit',
                'color': '#10b981'
            },
            {
                'accion': 'Inicio de Sesión',
                'descripcion': 'Acceso desde navegador web',
                'fecha': '2024-02-15 09:00:00',
                'estado': 'Registrado',
                'estado_clase': 'status-info',
                'icono': 'fas fa-sign-in-alt',
                'color': '#6b7280'
            }
        ]
        actividades_usuario.extend(actividades_ejemplo[:5-len(actividades_usuario)])
    
    # Datos del usuario con información dinámica
    usuario_data = {
        'nombre': usuario_actual.nombre if usuario_actual else 'Usuario Demo',
        'cargo': usuario_actual.cargo if usuario_actual else 'Cargo Demo',
        'email': usuario_actual.email if usuario_actual else 'demo@pacta.com',
        'telefono': '+57 300 123 4567',  # Campo fijo por ahora
        'dias_activo': 245,  # Campo calculado por ahora
        'nivel_acceso': 'Admin',  # Campo fijo por ahora
        'contratos_creados': len(contratos_usuario),
        'reportes_generados': reportes_mes,
        'ultimo_acceso': 'Hoy 09:30',  # Campo calculado por ahora
        'sesiones_mes': 28  # Campo calculado por ahora
    }
    
    # Estadísticas generales dinámicas
    estadisticas = {
        'contratos_activos': estadisticas_contratos['contratos_activos'],
        'valor_total': f"{estadisticas_contratos['valor_total']:,.0f}",
        'proximos_vencer': estadisticas_contratos['proximos_vencer'],
        'reportes_generados': reportes_mes
    }
    
    return render_template('usuario.html', usuario=usuario_data, estadisticas=estadisticas, actividades=actividades_usuario)

# API para obtener datos de contratos
@app.route('/api/contratos')
def api_contratos():
    # Obtener contratos reales de la base de datos
    contratos_db = Contrato.get_all()
    contratos_data = []
    
    for contrato in contratos_db:
        cliente = Cliente.get_by_id(contrato.cliente_id)
        usuario = Usuario.get_by_id(contrato.usuario_responsable_id)
        
        # Convertir fechas de string a date si es necesario
        if isinstance(contrato.fecha_inicio, str):
            try:
                fecha_inicio = datetime.strptime(contrato.fecha_inicio, '%Y-%m-%d').date()
            except ValueError:
                fecha_inicio = datetime.now().date()
        else:
            fecha_inicio = contrato.fecha_inicio
            
        if isinstance(contrato.fecha_fin, str):
            try:
                fecha_fin = datetime.strptime(contrato.fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                fecha_fin = datetime.now().date()
        else:
            fecha_fin = contrato.fecha_fin
        
        contratos_data.append({
            'id': contrato.numero_contrato,
            'nombre': contrato.titulo,
            'tipo': contrato.tipo_contrato,
            'proveedor': cliente.nombre if cliente else 'N/A',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_vencimiento': fecha_fin.strftime('%Y-%m-%d'),
            'valor': contrato.monto_actual,
            'estado': contrato.estado.title(),
            'responsable': usuario.nombre if usuario else 'N/A'
        })
    
    return jsonify(contratos_data)

# API para estadísticas generales
# Ruta para crear usuarios (solo admin)
@app.route('/crear_usuario', methods=['POST'])
@admin_required
def crear_usuario():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        telefono = request.form.get('telefono', '')
        cargo = request.form.get('cargo', '')
        departamento = request.form.get('departamento', '')
        es_admin = request.form.get('es_admin') == 'on'
        
        # Validaciones
        if not all([nombre, email, username, password]):
            return jsonify({'success': False, 'message': 'Todos los campos obligatorios deben ser completados'})
        
        # Verificar si el username ya existe
        usuario_existente = Usuario.get_by_username(username)
        if usuario_existente:
            return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'})
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            username=username,
            password=Usuario.hash_password(password),
            telefono=telefono,
            cargo=cargo,
            departamento=departamento,
            es_admin=es_admin
        )
        
        nuevo_usuario.save()
        
        # Registrar actividad
        actividad = ActividadSistema(
            usuario_id=session['user_id'],
            accion='Usuario Creado',
            tabla_afectada='usuarios',
            registro_id=nuevo_usuario.id,
            detalles=f'Nuevo usuario creado: {username} ({nombre})'
        )
        actividad.save()
        
        return jsonify({
            'success': True, 
            'message': f'Usuario {username} creado exitosamente',
            'usuario': {
                'id': nuevo_usuario.id,
                'nombre': nuevo_usuario.nombre,
                'username': nuevo_usuario.username,
                'email': nuevo_usuario.email,
                'cargo': nuevo_usuario.cargo,
                'departamento': nuevo_usuario.departamento,
                'es_admin': nuevo_usuario.es_admin
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al crear usuario: {str(e)}'})

@app.route('/usuarios_lista')
@admin_required
def usuarios_lista():
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener todos los usuarios
        usuarios = Usuario.get_all()
        
        # Estadísticas básicas
        estadisticas = {
            'total_usuarios': len(usuarios),
            'usuarios_activos': len([u for u in usuarios if hasattr(u, 'activo') and u.activo]),
            'administradores': len([u for u in usuarios if u.es_admin]),
            'usuarios_regulares': len([u for u in usuarios if not u.es_admin])
        }
        
        return render_template('usuarios_lista.html', 
                             usuario=usuario_actual,
                             usuarios=usuarios,
                             estadisticas=estadisticas)
    
    except Exception as e:
        flash('Error al cargar la lista de usuarios', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/estadisticas')
def api_estadisticas():
    contratos = Contrato.get_all()
    
    # Agrupar por tipo de contrato
    tipos_count = {}
    for contrato in contratos:
        tipo = contrato.tipo_contrato
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    # Agrupar por estado
    estados_count = {}
    for contrato in contratos:
        estado = contrato.estado.title()
        estados_count[estado] = estados_count.get(estado, 0) + 1
    
    return jsonify({
        'tipos_contrato': tipos_count,
        'estados_contrato': estados_count
    })

@app.route('/components/modals/user_modal')
@login_required
def user_modal():
    """Sirve el modal de usuario como componente"""
    return render_template('components/modals/user_modal.html')

@app.route('/components/modals/notifications_modal')
@login_required
def notifications_modal():
    """Sirve el modal de notificaciones como componente"""
    return render_template('components/modals/notifications_modal.html')

# API Routes para Notificaciones
@app.route('/api/notifications')
@api_login_required
def get_notifications():
    """Obtiene las notificaciones del usuario actual"""
    try:
        usuario_id = session['user_id']
        notificaciones = Notificacion.get_by_user(usuario_id)
        
        return jsonify({
            'success': True,
            'notifications': [notif.to_dict() for notif in notificaciones]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener notificaciones: {str(e)}'})

@app.route('/api/notifications/count')
@api_login_required
def get_notifications_count():
    """Obtiene el conteo de notificaciones no leídas"""
    try:
        usuario_id = session['user_id']
        count = Notificacion.count_unread(usuario_id)
        
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al contar notificaciones: {str(e)}'})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@api_login_required
def mark_notification_read(notification_id):
    """Marca una notificación como leída"""
    try:
        usuario_id = session['user_id']
        success = Notificacion.mark_as_read(notification_id, usuario_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Notificación marcada como leída'})
        else:
            return jsonify({'success': False, 'message': 'No se pudo marcar la notificación'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al marcar notificación: {str(e)}'})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@api_login_required
def mark_all_notifications_read():
    """Marca todas las notificaciones del usuario como leídas"""
    try:
        usuario_id = session['user_id']
        success = Notificacion.mark_all_as_read(usuario_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Todas las notificaciones marcadas como leídas'})
        else:
            return jsonify({'success': False, 'message': 'No se pudieron marcar las notificaciones'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al marcar notificaciones: {str(e)}'})

@app.route('/api/notifications/create-system', methods=['POST'])
@admin_required
def create_system_notification():
    """Crea una notificación del sistema (solo administradores)"""
    try:
        data = request.get_json()
        title = data.get('title')
        message = data.get('message')
        user_ids = data.get('user_ids', [])  # Lista de IDs de usuarios, vacía = todos
        
        if not title or not message:
            return jsonify({'success': False, 'message': 'Título y mensaje son requeridos'})
        
        # Si no se especifican usuarios, enviar a todos
        if not user_ids:
            usuarios = Usuario.get_all()
            user_ids = [u.id for u in usuarios]
        
        # Crear notificaciones para cada usuario
        for user_id in user_ids:
            Notificacion.create_system_notification(user_id, title, message)
        
        return jsonify({
            'success': True, 
            'message': f'Notificación enviada a {len(user_ids)} usuarios'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al crear notificación: {str(e)}'})

@app.route('/api/notifications/check-contracts', methods=['POST'])
@admin_required
def check_contract_reminders():
    """Ejecuta manualmente el sistema de recordatorios de contratos (solo administradores)"""
    try:
        reminder_system = ContractReminderSystem()
        
        # Verificar contratos individuales
        individual_notifications = reminder_system.check_expiring_contracts()
        
        # Crear recordatorios del sistema
        system_notifications = reminder_system.create_system_reminders()
        
        total_notifications = individual_notifications + system_notifications
        
        return jsonify({
            'success': True,
            'message': f'Verificación completada. {total_notifications} notificaciones creadas.',
            'details': {
                'individual_notifications': individual_notifications,
                'system_notifications': system_notifications,
                'total': total_notifications
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al verificar contratos: {str(e)}'})

def run_automatic_reminders():
    """Ejecuta automáticamente el sistema de recordatorios"""
    try:
        reminder_system = ContractReminderSystem()
        total_notifications = reminder_system.check_expiring_contracts()
        total_notifications += reminder_system.create_system_reminders()
        
        print(f"Recordatorios automáticos ejecutados: {total_notifications} notificaciones creadas")
        return total_notifications
    except Exception as e:
        print(f"Error en recordatorios automáticos: {str(e)}")
        return 0

if __name__ == '__main__':
    # Ejecutar la aplicación en modo desarrollo
    app.run(host='127.0.0.1', port=5000, debug=True)