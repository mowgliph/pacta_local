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
        # Obtener usuario actual (el decorador @login_required ya valida la sesión)
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener solo proveedores activos
        try:
            proveedores_db = Proveedor.get_all()
            proveedores = [p for p in proveedores_db if p.activo]
            print(f"Proveedores activos encontrados: {len(proveedores)}")
        except Exception as e:
            print(f"Error al obtener proveedores: {str(e)}")
            proveedores = []
            flash('Error al cargar la lista de proveedores', 'error')
        
        # Obtener contratos para estadísticas
        try:
            contratos = Contrato.get_all()
            # Filtrar contratos activos relacionados con proveedores
            contratos_proveedores = [
                c for c in contratos 
                if hasattr(c, 'proveedor_id') and c.proveedor_id is not None
                and hasattr(c, 'estado') and c.estado == 'activo'
            ]
            print(f"Contratos de proveedores activos encontrados: {len(contratos_proveedores)}")
        except Exception as e:
            print(f"Error al obtener contratos: {str(e)}")
            contratos_proveedores = []
        
        # Calcular estadísticas
        total_proveedores = len(proveedores)
        valor_total_proveedores = sum(
            c.monto_actual for c in contratos_proveedores 
            if hasattr(c, 'monto_actual') and c.monto_actual is not None
        )
        
        estadisticas = {
            'total_proveedores': total_proveedores,
            'proveedores_activos': total_proveedores,  # Ya filtramos solo activos
            'contratos_totales': len(contratos_proveedores),
            'valor_promedio': int(valor_total_proveedores / len(contratos_proveedores)) if contratos_proveedores else 0,
            'cambio_proveedores': 0,  # Valor temporal, se puede mejorar con histórico
            'porcentaje_activos': 100 if total_proveedores > 0 else 0,  # Todos están activos
            'valor_total': int(valor_total_proveedores)  # Añadido para consistencia con clientes
        }
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('proveedores.html', 
                            proveedores=proveedores,
                            estadisticas=estadisticas,
                            usuario=usuario_actual,
                            notificaciones_count=notificaciones_count)
                            
    except Exception as e:
        import traceback
        error_msg = f"Error en la página de proveedores: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        flash('Error al cargar la página de proveedores. Por favor, intente de nuevo más tarde.', 'error')
        return redirect(url_for('main.dashboard'))

# ===== RUTAS API PARA PROVEEDORES =====

@providers_bp.route('/api/proveedores', methods=['GET'])
@api_login_required
def api_get_proveedores():
    """API para obtener lista de proveedores"""
    try:
        # Obtener solo proveedores activos para mantener consistencia con clientes
        proveedores = Proveedor.get_all(activos_solo=True)
        
        proveedores_data = []
        for proveedor in proveedores:
            # Formato consistente de fecha
            fecha_creacion = proveedor.fecha_creacion.isoformat() if proveedor.fecha_creacion else None
            
            proveedores_data.append({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'tipo_proveedor': proveedor.tipo_proveedor,
                'rfc': proveedor.rfc or '',
                'email': proveedor.email or '',
                'telefono': proveedor.telefono or '',
                'direccion': proveedor.direccion or '',
                'contacto_principal': proveedor.contacto_principal or '',
                'activo': bool(proveedor.activo),
                'fecha_creacion': fecha_creacion
            })
        
        # Estructura de respuesta consistente con api_get_clientes
        return jsonify({
            'success': True,
            'proveedores': proveedores_data,
            'total': len(proveedores_data),
            'activos': len(proveedores_data)  # Ya están filtrados solo activos
        })
        
    except Exception as e:
        # Manejo de errores consistente
        error_msg = f'Error al obtener proveedores: {str(e)}'
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@providers_bp.route('/api/proveedores', methods=['POST'])
@api_login_required
def api_create_proveedor():
    """API para crear un nuevo proveedor
    
    Parámetros (JSON):
    - nombre (obligatorio): Nombre del proveedor
    - tipo_proveedor: Tipo de proveedor (default: 'servicio')
    - rfc: RFC del proveedor
    - email: Correo electrónico
    - telefono: Número de teléfono
    - direccion: Dirección física
    - contacto_principal: ID o JSON de contacto principal
    - activo: Estado del proveedor (default: True)
    
    Returns:
        JSON con el resultado de la operación
    """
    try:
        data = request.get_json() or {}
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'El nombre es requerido'
            }), 400
        
        # Crear nuevo proveedor con valores por defecto
        proveedor = Proveedor(
            nombre=data['nombre'],
            tipo_proveedor=data.get('tipo_proveedor', 'servicio'),
            rfc=data.get('rfc', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            direccion=data.get('direccion', ''),
            contacto_principal=data.get('contacto_principal', ''),
            activo=bool(data.get('activo', True))
        )
        
        # Guardar en la base de datos
        proveedor.save()
        
        # Estructura de respuesta consistente
        return jsonify({
            'success': True,
            'message': 'Proveedor creado exitosamente',
            'proveedor_id': proveedor.id
        }), 201  # 201 Created
        
    except Exception as e:
        # Manejo de errores consistente
        error_msg = f'Error al crear proveedor: {str(e)}'
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@providers_bp.route('/api/proveedores/<int:proveedor_id>', methods=['PUT'])
@api_login_required
def api_update_proveedor(proveedor_id):
    """API para actualizar un proveedor existente
    
    Parámetros (JSON):
    - nombre: Nuevo nombre del proveedor
    - tipo_proveedor: Tipo de proveedor
    - rfc: RFC del proveedor
    - email: Correo electrónico
    - telefono: Número de teléfono
    - direccion: Dirección física
    - contacto_principal: ID o JSON de contacto principal
    - activo: Estado del proveedor
    
    Returns:
        JSON con el resultado de la operación
    """
    try:
        data = request.get_json() or {}
        proveedor = Proveedor.get_by_id(proveedor_id)
        
        if not proveedor:
            return jsonify({
                'success': False,
                'message': 'No se encontró el proveedor especificado'
            }), 404
        
        # Lista de campos actualizables
        campos_actualizables = [
            'nombre', 'tipo_proveedor', 'rfc', 'email', 
            'telefono', 'direccion', 'contacto_principal', 'activo'
        ]
        
        # Actualizar solo los campos que vienen en la petición
        actualizaciones = {}
        for campo in campos_actualizables:
            if campo in data:
                setattr(proveedor, campo, data[campo])
                actualizaciones[campo] = data[campo]
        
        # Guardar cambios si hay actualizaciones
        if actualizaciones:
            proveedor.save()
            
        return jsonify({
            'success': True,
            'message': 'Proveedor actualizado exitosamente'
        })
        
    except Exception as e:
        error_msg = f'Error al actualizar proveedor: {str(e)}'
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@providers_bp.route('/api/proveedores/<int:proveedor_id>', methods=['DELETE'])
@api_login_required
def api_delete_proveedor(proveedor_id):
    """API para eliminar un proveedor
    
    Args:
        proveedor_id (int): ID del proveedor a eliminar
        
    Returns:
        JSON con el resultado de la operación
    """
    try:
        # Verificar si el proveedor existe
        proveedor = Proveedor.get_by_id(proveedor_id)
        if not proveedor:
            return jsonify({
                'success': False,
                'message': 'No se encontró el proveedor especificado'
            }), 404
        
        # Verificar si el proveedor tiene contratos activos
        contratos = Contrato.get_all()
        contratos_activos = [
            c for c in contratos 
            if hasattr(c, 'proveedor_id') and c.proveedor_id == proveedor_id 
            and hasattr(c, 'estado') and c.estado == 'activo'
        ]
        
        if contratos_activos:
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar el proveedor porque tiene contratos activos'
            }), 409  # 409 Conflict
        
        # Eliminar el proveedor
        proveedor.delete()
        
        return jsonify({
            'success': True,
            'message': 'Proveedor eliminado exitosamente'
        })
        
    except Exception as e:
        error_msg = f'Error al eliminar proveedor: {str(e)}'
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

# ===== API PARA RESUMEN DE PROVEEDORES =====

@providers_bp.route('/api/providers-summary', methods=['GET'])
@api_login_required
def api_get_providers_summary():
    """API para obtener un resumen de proveedores
    
    Returns:
        JSON con estadísticas y lista resumida de proveedores
    """
    try:
        # Obtener solo proveedores activos
        proveedores = Proveedor.get_all(activos_solo=True)
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Filtrar contratos activos de proveedores
        contratos_activos = [
            c for c in contratos 
            if hasattr(c, 'proveedor_id') and c.proveedor_id is not None
            and hasattr(c, 'estado') and c.estado == 'activo'
        ]
        
        # Calcular estadísticas generales
        total_proveedores = len(proveedores)
        total_contratos = len(contratos_activos)
        valor_total = sum(c.monto_actual for c in contratos_activos if hasattr(c, 'monto_actual') and c.monto_actual is not None)
        
        # Preparar lista de proveedores con estadísticas (máximo 10)
        proveedores_data = []
        for proveedor in proveedores[:10]:
            # Contratos del proveedor
            contratos_proveedor = [
                c for c in contratos_activos 
                if hasattr(c, 'proveedor_id') and c.proveedor_id == proveedor.id
            ]
            
            # Calcular valor total de contratos del proveedor
            valor_proveedor = sum(
                c.monto_actual for c in contratos_proveedor 
                if hasattr(c, 'monto_actual') and c.monto_actual is not None
            )
            
            proveedores_data.append({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'tipo': proveedor.tipo_proveedor,
                'contratos': len(contratos_proveedor),
                'valor_total': valor_proveedor,
                'ultima_actualizacion': datetime.now().isoformat()
            })
        
        # Ordenar proveedores por valor total (mayor a menor)
        proveedores_data.sort(key=lambda x: x['valor_total'], reverse=True)
        
        # Estructura de respuesta consistente
        return jsonify({
            'success': True,
            'data': {
                'estadisticas': {
                    'total_proveedores': total_proveedores,
                    'total_contratos': total_contratos,
                    'valor_total_contratos': valor_total,
                    'promedio_por_proveedor': valor_total / total_proveedores if total_proveedores > 0 else 0
                },
                'proveedores': proveedores_data,
                'metadata': {
                    'total': len(proveedores_data),
                    'timestamp': datetime.now().isoformat()
                }
            }
        })
        
    except Exception as e:
        error_msg = f'Error al obtener resumen de proveedores: {str(e)}'
        return jsonify({
            'success': False,
            'error': {
                'code': 'PROVIDERS_SUMMARY_ERROR',
                'message': error_msg
            }
        }), 500