from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import random
from database.models import Usuario, Cliente, Contrato, Suplemento, ActividadSistema
from services.system_metrics import get_system_metrics

main_bp = Blueprint('main', __name__)

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

# Ruta principal - Redirigir a dashboard
@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.dashboard'))

# Ruta del Dashboard Principal
@main_bp.route('/dashboard')
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

@main_bp.route('/contratos')
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

@main_bp.route('/suplementos')
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

@main_bp.route('/reportes')
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

@main_bp.route('/configuracion')
@admin_required
def configuracion():
    # Generar estadísticas para la página de configuración
    estadisticas = {
        'usuarios_activos': 24,
        'configuraciones': 12,
        'ultimo_backup': 'Ayer',
        'espacio_usado': '68%'
    }
    
    # Obtener métricas del servidor
    metricas_servidor = get_system_metrics()
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    return render_template('configuracion.html', 
                         estadisticas=estadisticas,
                         metricas_servidor=metricas_servidor,
                         usuario=usuario_actual)

@main_bp.route('/api/system-metrics')
def get_system_metrics_api():
    """API endpoint para obtener métricas del sistema en tiempo real"""
    try:
        # Obtener métricas del sistema
        metrics = get_system_metrics()
        
        # Agregar información adicional de la aplicación
        app_info = {
            'version': 'v2.1.0',
            'status': 'operational',
            'database_type': 'SQLite',
            'last_backup': 'N/A'  # Esto se podría obtener de la configuración
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'app_info': app_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500