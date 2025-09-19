from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
import random
from database.models import Usuario, Cliente, Contrato, Suplemento, ActividadSistema, Notificacion
from services.system_metrics import get_system_metrics
from services.config_metrics import get_config_metrics
from .decorators import login_required, admin_required
from .utils import get_notificaciones_count, get_current_user_id

main_bp = Blueprint('main', __name__)

def obtener_estadisticas_contratos():
    """Obtiene estadísticas de contratos desde la base de datos"""
    try:
        contratos = Contrato.get_all()
        
        if not contratos:
            return {
                'total_contratos': 0,
                'contratos_activos': 0,
                'valor_total': 0,
                'proximos_vencer': 0
            }
        
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
    except Exception as e:
        return {
            'total_contratos': 0,
            'contratos_activos': 0,
            'valor_total': 0,
            'proximos_vencer': 0
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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('dashboard.html', 
                         estadisticas=estadisticas_completas, 
                         contratos=contratos_recientes,
                         actividad_reciente=actividad_reciente,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count,
                         page_title='Dashboard',
                         page_subtitle='Panel de control y métricas del sistema',
                         page_icon='fas fa-tachometer-alt',
                         show_notifications=True,
                         show_user_menu=True)



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
    try:
        suplementos = Suplemento.get_all()
        
        total_suplementos = len(suplementos)
        suplementos_aprobados = len([s for s in suplementos if s and hasattr(s, 'estado') and s.estado == 'aprobado'])
        suplementos_pendientes = len([s for s in suplementos if s and hasattr(s, 'estado') and s.estado == 'pendiente'])
        suplementos_rechazados = len([s for s in suplementos if s and hasattr(s, 'estado') and s.estado == 'rechazado'])
        
        # Calcular porcentajes
        porcentaje_aprobados = round((suplementos_aprobados / total_suplementos * 100) if total_suplementos > 0 else 0, 1)
        porcentaje_pendientes = round((suplementos_pendientes / total_suplementos * 100) if total_suplementos > 0 else 0, 1)
        
        # Calcular valor total de modificaciones
        valor_total_modificaciones = sum([s.monto_modificacion for s in suplementos 
                                        if s and hasattr(s, 'estado') and hasattr(s, 'monto_modificacion') 
                                        and s.estado == 'aprobado' and s.monto_modificacion is not None] or [0])
        
        # Estadísticas por tipo de modificación
        ampliacion_monto = len([s for s in suplementos 
                              if s and hasattr(s, 'tipo_modificacion') and s.tipo_modificacion 
                              and 'monto' in str(s.tipo_modificacion).lower()])
        
        extension_plazo = len([s for s in suplementos 
                             if s and hasattr(s, 'tipo_modificacion') and s.tipo_modificacion 
                             and 'plazo' in str(s.tipo_modificacion).lower()])
        
        modificacion_alcance = len([s for s in suplementos 
                                  if s and hasattr(s, 'tipo_modificacion') and s.tipo_modificacion 
                                  and 'alcance' in str(s.tipo_modificacion).lower()])
        
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
    except Exception as e:
        print(f"Error al obtener estadísticas de suplementos: {str(e)}")
        # Retornar valores por defecto en caso de error
        return {
            'total_suplementos': 0,
            'suplementos_aprobados': 0,
            'suplementos_pendientes': 0,
            'suplementos_rechazados': 0,
            'porcentaje_aprobados': 0,
            'porcentaje_pendientes': 0,
            'valor_total_modificaciones': 0,
            'ampliacion_monto': 0,
            'extension_plazo': 0,
            'modificacion_alcance': 0,
            'otros_tipos': 0
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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('suplementos.html', 
                         suplementos=suplementos, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count,
                         page_title='Suplementos',
                         page_subtitle='Gestión y administración de suplementos contractuales',
                         page_icon='fas fa-file-plus',
                         show_notifications=True,
                         show_user_menu=True)

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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('reportes.html', 
                         reportes=reportes_data, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count,
                         page_title='Reportes',
                         page_subtitle='Generación y gestión de reportes del sistema',
                         page_icon='fas fa-chart-bar',
                         show_notifications=True,
                         show_user_menu=True)

@main_bp.route('/configuracion')
@admin_required
def configuracion():
    # Obtener métricas dinámicas para la página de configuración
    estadisticas = get_config_metrics()
    
    # Obtener métricas del servidor
    metricas_servidor = get_system_metrics()
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('configuracion.html', 
                         estadisticas=estadisticas,
                         metricas_servidor=metricas_servidor,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count,
                         page_title='Configuración',
                         page_subtitle='Configuración del sistema y administración',
                         page_icon='fas fa-cog',
                         show_notifications=True,
                         show_user_menu=True)

@main_bp.route('/backup')
@login_required
def backup():
    usuario = Usuario.get_by_id(session['user_id'])
    notificaciones_count = get_notificaciones_count()
    return render_template('backup_management.html', usuario=usuario, notificaciones_count=notificaciones_count)



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

@main_bp.route('/contratos-vencidos')
@login_required
def contratos_vencidos():
    """Redirige a la página de contratos vencidos"""
    return redirect(url_for('contratos.contratos_vencidos'))