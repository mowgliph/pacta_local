from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify, request
from datetime import datetime, timedelta
from database.models import Usuario, Cliente, Contrato, Notificacion, Proveedor
from .decorators import login_required, admin_required, api_login_required
from .utils import get_notificaciones_count, get_current_user_id, create_success_response, create_error_response

providers_bp = Blueprint('providers', __name__)

# ===== RUTAS DE PROVEEDORES =====

@providers_bp.route('/api/proveedores/personas-recientes', methods=['GET'])
@api_login_required
def api_get_personas_recientes_proveedores():
    """Obtiene las últimas 5 personas responsables relacionadas con proveedores"""
    try:
        from database.models.persona_responsable import PersonaResponsable
        import json
        
        # Obtener todos los proveedores activos con contactos
        proveedores = Proveedor.get_all(activos_solo=True)
        
        # Recopilar todos los IDs de personas de contacto
        persona_ids = set()
        proveedor_persona_map = {}  # Para mapear persona_id -> proveedor_info
        
        for proveedor in proveedores:
            if proveedor.contacto_principal:
                try:
                    # El contacto_principal puede ser JSON con IDs de personas
                    if proveedor.contacto_principal.startswith('[') or proveedor.contacto_principal.startswith('{'):
                        contactos = json.loads(proveedor.contacto_principal)
                        if isinstance(contactos, list):
                            for persona_id in contactos:
                                persona_ids.add(int(persona_id))
                                proveedor_persona_map[int(persona_id)] = {
                                    'proveedor_id': proveedor.id,
                                    'proveedor_nombre': proveedor.nombre,
                                    'proveedor_tipo': proveedor.tipo_proveedor
                                }
                        elif isinstance(contactos, dict):
                            for key, persona_id in contactos.items():
                                persona_ids.add(int(persona_id))
                                proveedor_persona_map[int(persona_id)] = {
                                    'proveedor_id': proveedor.id,
                                    'proveedor_nombre': proveedor.nombre,
                                    'proveedor_tipo': proveedor.tipo_proveedor
                                }
                    else:
                        # Podría ser un ID simple
                        try:
                            persona_id = int(proveedor.contacto_principal)
                            persona_ids.add(persona_id)
                            proveedor_persona_map[persona_id] = {
                                'proveedor_id': proveedor.id,
                                'proveedor_nombre': proveedor.nombre,
                                'proveedor_tipo': proveedor.tipo_proveedor
                            }
                        except ValueError:
                            pass
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Obtener las personas responsables
        if persona_ids:
            personas = PersonaResponsable.get_by_ids(list(persona_ids))
            
            # Combinar información de personas con proveedores
            personas_con_proveedor = []
            for persona in personas:
                if persona.id in proveedor_persona_map:
                    proveedor_info = proveedor_persona_map[persona.id]
                    # Manejar fecha_creacion que puede ser string o datetime
                    fecha_creacion = None
                    if persona.fecha_creacion:
                        if isinstance(persona.fecha_creacion, str):
                            fecha_creacion = persona.fecha_creacion
                        else:
                            fecha_creacion = persona.fecha_creacion.isoformat()
                    
                    personas_con_proveedor.append({
                        'id': persona.id,
                        'nombre': persona.nombre,
                        'cargo': persona.cargo,
                        'telefono': persona.telefono,
                        'email': persona.email,
                        'es_principal': persona.es_principal,
                        'fecha_creacion': fecha_creacion,
                        'proveedor_id': proveedor_info['proveedor_id'],
                        'proveedor_nombre': proveedor_info['proveedor_nombre'],
                        'proveedor_tipo': proveedor_info['proveedor_tipo']
                    })
            
            # Ordenar por fecha de creación (más recientes primero) y tomar las últimas 5
            personas_con_proveedor.sort(key=lambda x: x['fecha_creacion'] or '1900-01-01', reverse=True)
            personas_recientes = personas_con_proveedor[:5]
        else:
            personas_recientes = []
        
        return jsonify({
            'success': True,
            'data': personas_recientes
        })
        
    except Exception as e:
        print(f"Error al obtener personas recientes de proveedores: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener personas recientes: {str(e)}'
        }), 500

@providers_bp.route('/api/proveedores/estadisticas', methods=['GET'])
@api_login_required
def api_get_estadisticas_proveedores():
    """API para obtener estadísticas de proveedores"""
    try:
        # Fechas para comparación
        hoy = datetime.now()
        inicio_mes_actual = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year-1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month-1)
        
        # Obtener todos los proveedores
        proveedores = Proveedor.get_all()
        
        # Obtener contratos para estadísticas (los contratos no están directamente relacionados con proveedores)
        contratos = Contrato.get_all()
        
        # Estadísticas actuales
        total_proveedores = len(proveedores)
        proveedores_activos = len([p for p in proveedores if p.activo])
        
        # Manejar fecha_creacion que puede ser string o datetime
        proveedores_mes_actual = []
        for p in proveedores:
            if p.fecha_creacion:
                try:
                    if isinstance(p.fecha_creacion, str):
                        fecha_prov = datetime.fromisoformat(p.fecha_creacion.replace('Z', '+00:00'))
                    else:
                        fecha_prov = p.fecha_creacion
                    
                    if fecha_prov >= inicio_mes_actual:
                        proveedores_mes_actual.append(p)
                except (ValueError, AttributeError):
                    continue
        
        # Estadísticas del mes anterior
        proveedores_mes_anterior = [p for p in proveedores if p not in proveedores_mes_actual]
        total_proveedores_mes_anterior = len(proveedores_mes_anterior)
        
        # Calcular cambios
        cambio_proveedores = len(proveedores_mes_actual)
        
        # Porcentaje de proveedores activos
        porcentaje_activos = (proveedores_activos / total_proveedores * 100) if total_proveedores > 0 else 0
        
        # Para contratos, simplemente mostrar estadísticas generales
        contratos_activos = [c for c in contratos if c.estado == 'activo']
        valor_total_contratos = sum([c.monto_actual for c in contratos_activos if c.monto_actual])
        
        estadisticas = {
            'total_proveedores': total_proveedores,
            'proveedores_activos': proveedores_activos,
            'contratos_totales': len(contratos),
            'valor_promedio': int(valor_total_contratos / len(contratos_activos)) if contratos_activos else 0,
            'valor_total': int(valor_total_contratos),
            'cambio_proveedores': cambio_proveedores,
            'cambio_contratos': 0,  # No hay relación directa entre contratos y proveedores
            'porcentaje_activos': round(porcentaje_activos, 1)
        }
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500

@providers_bp.route('/proveedores')
@login_required
def proveedores():
    """Página de gestión de proveedores"""
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener todos los proveedores
        proveedores = Proveedor.get_all()
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Calcular estadísticas de proveedores
        total_proveedores = len(proveedores)
        proveedores_activos = len([p for p in proveedores if p.activo])
        contratos_proveedores = [c for c in contratos if any(p.id == c.proveedor_id for p in proveedores) if hasattr(c, 'proveedor_id')]
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

# ===== RUTAS API PARA PROVEEDORES =====

@providers_bp.route('/api/proveedores', methods=['GET'])
@api_login_required
def api_get_proveedores():
    """API para obtener lista de proveedores"""
    try:
        proveedores = Proveedor.get_all(activos_solo=False)
        
        proveedores_data = []
        for proveedor in proveedores:
            # Manejar fecha_creacion que puede ser string o datetime
            fecha_creacion = None
            if proveedor.fecha_creacion:
                if isinstance(proveedor.fecha_creacion, str):
                    try:
                        fecha_creacion = datetime.fromisoformat(proveedor.fecha_creacion.replace('Z', '+00:00')).isoformat()
                    except:
                        fecha_creacion = proveedor.fecha_creacion
                else:
                    fecha_creacion = proveedor.fecha_creacion.isoformat()
            
            proveedores_data.append({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'tipo_proveedor': proveedor.tipo_proveedor,
                'rfc': proveedor.rfc,
                'email': proveedor.email,
                'telefono': proveedor.telefono,
                'direccion': proveedor.direccion,
                'contacto_principal': proveedor.contacto_principal,
                'activo': proveedor.activo,
                'fecha_creacion': fecha_creacion
            })
        
        return jsonify({
            'success': True,
            'proveedores': proveedores_data
        })
    except Exception as e:
        print(f"Error en api_get_proveedores: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener proveedores: {str(e)}'
        }), 500

@providers_bp.route('/api/proveedores', methods=['POST'])
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
        proveedor = Proveedor(
            nombre=data.get('nombre'),
            tipo_proveedor=data.get('tipo_proveedor', 'servicio'),
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

@providers_bp.route('/api/proveedores/<int:proveedor_id>', methods=['PUT'])
@api_login_required
def api_update_proveedor(proveedor_id):
    """API para actualizar un proveedor"""
    try:
        data = request.get_json()
        proveedor = Proveedor.get_by_id(proveedor_id)
        
        if not proveedor:
            return jsonify({
                'success': False,
                'message': 'Proveedor no encontrado'
            }), 404
        
        # Actualizar campos
        if 'nombre' in data:
            proveedor.nombre = data['nombre']
        if 'tipo_proveedor' in data:
            proveedor.tipo_proveedor = data['tipo_proveedor']
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

@providers_bp.route('/api/proveedores/<int:proveedor_id>', methods=['DELETE'])
@api_login_required
def api_delete_proveedor(proveedor_id):
    """API para eliminar un proveedor"""
    try:
        proveedor = Proveedor.get_by_id(proveedor_id)
        
        if not proveedor:
            return jsonify({
                'success': False,
                'message': 'Proveedor no encontrado'
            }), 404
        
        # Verificar si el proveedor tiene contratos activos
        contratos = Contrato.get_all()
        contratos_activos = [c for c in contratos if hasattr(c, 'proveedor_id') and c.proveedor_id == proveedor_id and c.estado == 'activo']
        
        if contratos_activos:
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar el proveedor porque tiene contratos activos'
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

# ===== API PARA RESUMEN DE PROVEEDORES =====

@providers_bp.route('/api/providers-summary', methods=['GET'])
@api_login_required
def api_get_providers_summary():
    """API para obtener resumen de proveedores para el componente providers-clients-block"""
    try:
        # Obtener proveedores
        proveedores = Proveedor.get_all()
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Preparar datos de proveedores con estadísticas
        providers_data = []
        for proveedor in proveedores[:10]:  # Limitar a 10 proveedores principales
            # Contar contratos relacionados (simulado ya que no hay relación directa)
            contratos_count = len([c for c in contratos if hasattr(c, 'proveedor_id') and c.proveedor_id == proveedor.id])
            
            # Calcular valor total (simulado)
            total_value = sum([c.monto_actual for c in contratos if hasattr(c, 'proveedor_id') and c.proveedor_id == proveedor.id and c.estado == 'activo'])
            
            providers_data.append({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'industria': proveedor.tipo_proveedor,
                'contratos_count': contratos_count,
                'total_value': total_value,
                'activo': proveedor.activo
            })
        
        return jsonify({
            'success': True,
            'providers': providers_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener resumen de proveedores: {str(e)}'
        }), 500