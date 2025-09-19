from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from datetime import datetime, timedelta
from database.models import Suplemento, Contrato, Usuario, ActividadSistema
from .decorators import login_required, admin_required
from .utils import get_notificaciones_count
from database.database import db_manager

# Crear el Blueprint para las rutas de suplementos
suplementos_bp = Blueprint('suplementos', __name__, url_prefix='/suplementos')

def obtener_todos_suplementos():
    """Obtiene todos los suplementos con información enriquecida"""
    try:
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
    except Exception as e:
        print(f"Error al obtener suplementos: {str(e)}")
        return []

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

@suplementos_bp.route('/')
@login_required
def index():
    """Página principal de gestión de suplementos"""
    # Obtener todos los suplementos
    suplementos_lista = obtener_todos_suplementos()
    
    # Obtener estadísticas
    estadisticas = obtener_estadisticas_suplementos()
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('suplementos.html', 
                         suplementos=suplementos_lista, 
                         estadisticas=estadisticas,
                         usuario=usuario_actual,
                         notificaciones_count=notificaciones_count,
                         page_title='Suplementos',
                         page_subtitle='Gestión y administración de suplementos contractuales',
                         page_icon='fas fa-file-plus',
                         show_notifications=True,
                         show_user_menu=True)

@suplementos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crear un nuevo suplemento"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            contrato_id = request.form.get('contrato_id')
            tipo_modificacion = request.form.get('tipo_modificacion')
            descripcion = request.form.get('descripcion')
            monto_modificacion = float(request.form.get('monto_modificacion', 0))
            fecha_modificacion = request.form.get('fecha_modificacion')
            
            # Crear el suplemento
            suplemento = Suplemento(
                contrato_id=contrato_id,
                numero_suplemento=f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                tipo_modificacion=tipo_modificacion,
                descripcion=descripcion,
                monto_modificacion=monto_modificacion,
                fecha_modificacion=fecha_modificacion,
                usuario_autoriza_id=session['user_id'],
                estado='pendiente',
                fecha_creacion=datetime.now()
            )
            
            # Guardar en la base de datos
            suplemento.save()
            
            # Registrar actividad
            ActividadSistema.registrar(
                usuario_id=session['user_id'],
                modulo='Suplementos',
                accion='Crear',
                detalles=f"Se creó el suplemento {suplemento.numero_suplemento}"
            )
            
            flash('Suplemento creado correctamente', 'success')
            return redirect(url_for('suplementos.index'))
            
        except Exception as e:
            print(f"Error al crear suplemento: {str(e)}")
            flash('Error al crear el suplemento. Por favor, intente nuevamente.', 'error')
    
    # Si es GET o hay error, mostrar el formulario
    return render_template('suplementos/crear.html',
                         page_title='Crear Suplemento',
                         page_icon='fas fa-plus')

@suplementos_bp.route('/<int:suplemento_id>')
@login_required
def detalle(suplemento_id):
    """Ver detalles de un suplemento específico"""
    suplemento = Suplemento.get_by_id(suplemento_id)
    if not suplemento:
        flash('Suplemento no encontrado', 'error')
        return redirect(url_for('suplementos.index'))
    
    # Enriquecer con información adicional
    contrato = Contrato.get_by_id(suplemento.contrato_id)
    usuario_autoriza = Usuario.get_by_id(suplemento.usuario_autoriza_id)
    
    return render_template('suplementos/detalle.html',
                         suplemento=suplemento,
                         contrato=contrato,
                         usuario_autoriza=usuario_autoriza,
                         page_title=f'Suplemento {suplemento.numero_suplemento}',
                         page_icon='fas fa-file-alt')

@suplementos_bp.route('/<int:suplemento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(suplemento_id):
    """Editar un suplemento existente"""
    suplemento = Suplemento.get_by_id(suplemento_id)
    if not suplemento:
        flash('Suplemento no encontrado', 'error')
        return redirect(url_for('suplementos.index'))
    
    if request.method == 'POST':
        try:
            # Actualizar datos del suplemento
            suplemento.tipo_modificacion = request.form.get('tipo_modificacion', suplemento.tipo_modificacion)
            suplemento.descripcion = request.form.get('descripcion', suplemento.descripcion)
            suplemento.monto_modificacion = float(request.form.get('monto_modificacion', suplemento.monto_modificacion))
            suplemento.fecha_modificacion = request.form.get('fecha_modificacion', suplemento.fecha_modificacion)
            
            # Guardar cambios
            suplemento.save()
            
            # Registrar actividad
            ActividadSistema.registrar(
                usuario_id=session['user_id'],
                modulo='Suplementos',
                accion='Editar',
                detalles=f"Se editó el suplemento {suplemento.numero_suplemento}"
            )
            
            flash('Suplemento actualizado correctamente', 'success')
            return redirect(url_for('suplementos.detalle', suplemento_id=suplemento.id))
            
        except Exception as e:
            print(f"Error al actualizar suplemento: {str(e)}")
            flash('Error al actualizar el suplemento. Por favor, intente nuevamente.', 'error')
    
    # Si es GET, mostrar el formulario con los datos actuales
    return render_template('suplementos/editar.html',
                         suplemento=suplemento,
                         page_title=f'Editar Suplemento {suplemento.numero_suplemento}',
                         page_icon='fas fa-edit')

@suplementos_bp.route('/<int:suplemento_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar(suplemento_id):
    """Eliminar un suplemento"""
    try:
        suplemento = Suplemento.get_by_id(suplemento_id)
        if not suplemento:
            flash('Suplemento no encontrado', 'error')
            return redirect(url_for('suplementos.index'))
        
        # Registrar actividad antes de eliminar
        ActividadSistema.registrar(
            usuario_id=session['user_id'],
            modulo='Suplementos',
            accion='Eliminar',
            detalles=f"Se eliminó el suplemento {suplemento.numero_superior}"
        )
        
        # Eliminar el suplemento
        Suplemento.eliminar(suplemento_id)
        
        flash('Suplemento eliminado correctamente', 'success')
        return redirect(url_for('suplementos.index'))
        
    except Exception as e:
        print(f"Error al eliminar suplemento: {str(e)}")
        flash('Error al eliminar el suplemento. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('suplementos.index'))

@suplementos_bp.route('/<int:suplemento_id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado(suplemento_id):
    """Cambiar el estado de un suplemento (aprobado/rechazado)"""
    try:
        suplemento = Suplemento.get_by_id(suplemento_id)
        if not suplemento:
            return jsonify({'success': False, 'message': 'Suplemento no encontrado'}), 404
        
        nuevo_estado = request.json.get('estado')
        if nuevo_estado not in ['aprobado', 'rechazado']:
            return jsonify({'success': False, 'message': 'Estado no válido'}), 400
        
        # Actualizar estado
        suplemento.estado = nuevo_estado
        suplemento.save()
        
        # Registrar actividad
        ActividadSistema.registrar(
            usuario_id=session['user_id'],
            modulo='Suplementos',
            accion='Cambiar Estado',
            detalles=f"Se cambió el estado del suplemento {suplemento.numero_suplemento} a {nuevo_estado}"
        )
        
        return jsonify({
            'success': True, 
            'message': f'Suplemento marcado como {nuevo_estado}',
            'estado': nuevo_estado
        })
        
    except Exception as e:
        print(f"Error al cambiar estado del suplemento: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al cambiar el estado del suplemento'}), 500
