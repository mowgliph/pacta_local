from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify, request
from datetime import datetime, timedelta
from database.models import Usuario, Cliente, Contrato, Notificacion
from .decorators import login_required, admin_required, api_login_required
from .utils import get_notificaciones_count, get_current_user_id, create_success_response, create_error_response

clients_bp = Blueprint('clients', __name__)

# ===== RUTAS DE CLIENTES =====

@clients_bp.route('/api/clientes/personas-recientes', methods=['GET'])
@api_login_required
def api_get_personas_recientes_clientes():
    """Obtiene las últimas 5 personas responsables relacionadas con clientes"""
    try:
        from database.models.persona_responsable import PersonaResponsable
        import json
        
        # Obtener todos los clientes activos con contactos
        clientes = Cliente.get_all()
        clientes_filtrados = [c for c in clientes if c.tipo_cliente == 'cliente' and c.activo]
        
        # Recopilar todos los IDs de personas de contacto
        persona_ids = set()
        cliente_persona_map = {}  # Para mapear persona_id -> cliente_info
        
        for cliente in clientes_filtrados:
            if cliente.contacto_principal:
                try:
                    # El contacto_principal puede ser JSON con IDs de personas
                    if cliente.contacto_principal.startswith('[') or cliente.contacto_principal.startswith('{'):
                        contactos = json.loads(cliente.contacto_principal)
                        if isinstance(contactos, list):
                            for persona_id in contactos:
                                persona_ids.add(int(persona_id))
                                cliente_persona_map[int(persona_id)] = {
                                    'cliente_id': cliente.id,
                                    'cliente_nombre': cliente.nombre,
                                    'cliente_tipo': cliente.tipo_cliente
                                }
                        elif isinstance(contactos, dict):
                            for key, persona_id in contactos.items():
                                persona_ids.add(int(persona_id))
                                cliente_persona_map[int(persona_id)] = {
                                    'cliente_id': cliente.id,
                                    'cliente_nombre': cliente.nombre,
                                    'cliente_tipo': cliente.tipo_cliente
                                }
                    else:
                        # Podría ser un ID simple
                        try:
                            persona_id = int(cliente.contacto_principal)
                            persona_ids.add(persona_id)
                            cliente_persona_map[persona_id] = {
                                'cliente_id': cliente.id,
                                'cliente_nombre': cliente.nombre,
                                'cliente_tipo': cliente.tipo_cliente
                            }
                        except ValueError:
                            pass
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Obtener las personas más recientes
        personas_recientes = []
        if persona_ids:
            personas = PersonaResponsable.get_all()
            personas_filtradas = [p for p in personas if p.id in persona_ids]
            personas_ordenadas = sorted(personas_filtradas, key=lambda x: x.fecha_creacion or datetime.min, reverse=True)[:5]
            
            for persona in personas_ordenadas:
                cliente_info = cliente_persona_map.get(persona.id, {})
                personas_recientes.append({
                    'id': persona.id,
                    'nombre': persona.nombre,
                    'apellido': persona.apellido,
                    'email': persona.email,
                    'telefono': persona.telefono,
                    'cargo': persona.cargo,
                    'fecha_creacion': persona.fecha_creacion.isoformat() if persona.fecha_creacion else None,
                    'cliente_id': cliente_info.get('cliente_id'),
                    'cliente_nombre': cliente_info.get('cliente_nombre'),
                    'cliente_tipo': cliente_info.get('cliente_tipo')
                })
        
        return jsonify({
            'success': True,
            'personas': personas_recientes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener personas recientes de clientes: {str(e)}'
        }), 500

@clients_bp.route('/api/clientes/estadisticas', methods=['GET'])
@api_login_required
def api_get_estadisticas_clientes():
    """API para obtener estadísticas de clientes"""
    try:
        # Obtener todos los clientes
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Calcular estadísticas básicas
        total_clientes = len(clientes)
        clientes_activos = len([c for c in clientes if c.activo])
        contratos_clientes = [c for c in contratos if any(cl.id == c.cliente_id for cl in clientes)]
        valor_total_clientes = sum([c.monto_actual for c in contratos_clientes if c.estado == 'activo'])
        
        # Calcular estadísticas adicionales
        porcentaje_activos = round((clientes_activos / total_clientes * 100) if total_clientes > 0 else 0, 1)
        valor_promedio = int(valor_total_clientes / len(contratos_clientes)) if contratos_clientes else 0
        
        # Estadísticas por mes (simuladas para el ejemplo)
        fecha_actual = datetime.now()
        mes_anterior = fecha_actual - timedelta(days=30)
        
        # Simular cambios mensuales
        cambio_clientes = max(0, int(total_clientes * 0.1))  # 10% de crecimiento simulado
        cambio_contratos = max(0, int(len(contratos_clientes) * 0.05))  # 5% de crecimiento simulado
        
        estadisticas = {
            'total_clientes': total_clientes,
            'clientes_activos': clientes_activos,
            'contratos_totales': len(contratos_clientes),
            'valor_promedio': valor_promedio,
            'porcentaje_activos': porcentaje_activos,
            'cambio_clientes': cambio_clientes,
            'cambio_contratos': cambio_contratos,
            'valor_total': valor_total_clientes
        }
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas de clientes: {str(e)}'
        }), 500

@clients_bp.route('/clientes')
@login_required
def clientes():
    """Página de gestión de clientes"""
    try:
        # Obtener usuario actual
        usuario_actual = Usuario.get_by_id(session['user_id'])
        
        # Obtener todos los clientes
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Calcular estadísticas de clientes
        total_clientes = len(clientes)
        clientes_activos = len([c for c in clientes if c.activo])
        contratos_clientes = [c for c in contratos if any(cl.id == c.cliente_id for cl in clientes)]
        valor_total_clientes = sum([c.monto_actual for c in contratos_clientes if c.estado == 'activo'])
        
        estadisticas = {
            'total_clientes': total_clientes,
            'clientes_activos': clientes_activos,
            'contratos_totales': len(contratos_clientes),
            'valor_promedio': int(valor_total_clientes / len(contratos_clientes)) if contratos_clientes else 0
        }
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('clientes.html', 
                             clientes=clientes,
                             estadisticas=estadisticas,
                             usuario=usuario_actual,
                             notificaciones_count=notificaciones_count)
    except Exception as e:
        flash(f'Error al cargar clientes: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

# ===== RUTAS API PARA CLIENTES =====

@clients_bp.route('/api/clientes', methods=['GET'])
@api_login_required
def api_get_clientes():
    """API para obtener lista de clientes"""
    try:
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        clientes_data = []
        for cliente in clientes:
            try:
                cliente_data = {
                    'id': getattr(cliente, 'id', None),
                    'nombre': getattr(cliente, 'nombre', 'Sin nombre'),
                    'rfc': getattr(cliente, 'rfc', ''),
                    'email': getattr(cliente, 'email', ''),
                    'telefono': getattr(cliente, 'telefono', ''),
                    'direccion': getattr(cliente, 'direccion', ''),
                    'contacto_principal': getattr(cliente, 'contacto_principal', ''),
                    'activo': getattr(cliente, 'activo', True)
                }
                
                # Manejar fecha_creacion de manera segura
                fecha_creacion = getattr(cliente, 'fecha_creacion', None)
                if hasattr(fecha_creacion, 'isoformat'):
                    cliente_data['fecha_creacion'] = fecha_creacion.isoformat()
                else:
                    cliente_data['fecha_creacion'] = None
                    
                clientes_data.append(cliente_data)
                
            except Exception as e:
                print(f"Error procesando cliente {getattr(cliente, 'id', 'desconocido')}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'clientes': clientes_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener clientes: {str(e)}'
        }), 500

@clients_bp.route('/api/clientes', methods=['POST'])
@api_login_required
def api_create_cliente():
    """API para crear un nuevo cliente"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return jsonify({
                'success': False,
                'message': 'El nombre es requerido'
            }), 400
        
        # Crear nuevo cliente
        cliente = Cliente(
            nombre=data.get('nombre'),
            tipo_cliente='cliente',
            rfc=data.get('rfc', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            contacto_principal=data.get('contacto_principal', ''),
            activo=data.get('activo', True)
        )
        
        cliente.save()
        
        return jsonify({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'cliente_id': cliente.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear cliente: {str(e)}'
        }), 500

@clients_bp.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
@api_login_required
def api_update_cliente(cliente_id):
    """API para actualizar un cliente"""
    try:
        data = request.get_json()
        cliente = Cliente.get_by_id(cliente_id)
        
        if not cliente or cliente.tipo_cliente != 'cliente':
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado'
            }), 404
        
        # Actualizar campos
        if 'nombre' in data:
            cliente.nombre = data['nombre']
        if 'rfc' in data:
            cliente.rfc = data['rfc']
        if 'email' in data:
            cliente.email = data['email']
        if 'telefono' in data:
            cliente.telefono = data['telefono']
        if 'direccion' in data:
            cliente.direccion = data['direccion']
        if 'contacto_principal' in data:
            cliente.contacto_principal = data['contacto_principal']
        if 'activo' in data:
            cliente.activo = data['activo']
        
        cliente.save()
        
        return jsonify({
            'success': True,
            'message': 'Cliente actualizado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar cliente: {str(e)}'
        }), 500

@clients_bp.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
@api_login_required
def api_delete_cliente(cliente_id):
    """API para eliminar un cliente"""
    try:
        cliente = Cliente.get_by_id(cliente_id)
        
        if not cliente or cliente.tipo_cliente != 'cliente':
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado'
            }), 404
        
        # Verificar si el cliente tiene contratos activos
        contratos = Contrato.get_all()
        contratos_activos = [c for c in contratos if c.cliente_id == cliente_id and c.estado == 'activo']
        
        if contratos_activos:
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar el cliente porque tiene contratos activos'
            }), 400
        
        cliente.delete()
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar cliente: {str(e)}'
        }), 500

# ===== API PARA RESUMEN DE CLIENTES =====

@clients_bp.route('/api/clients-summary', methods=['GET'])
@api_login_required
def api_get_clients_summary():
    """API para obtener resumen de clientes para el componente providers-clients-block"""
    try:
        from datetime import datetime
        
        # Obtener clientes
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        # Obtener contratos para estadísticas
        contratos = Contrato.get_all()
        
        # Preparar datos de clientes con estadísticas
        clients_data = []
        for cliente in clientes:  # No limitamos aquí para permitir ordenamiento completo
            # Contar contratos activos del cliente
            contratos_activos = [
                c for c in contratos 
                if c.cliente_id == cliente.id and c.estado == 'activo'
            ]
            
            # Calcular valor total de contratos activos
            total_value = sum([
                c.monto_actual 
                for c in contratos_activos 
                if hasattr(c, 'monto_actual') and c.monto_actual is not None
            ])
            
            client_data = {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'contracts_count': len(contratos_activos),
                'total_contracts': len(contratos_activos),  # Para compatibilidad
                'valor_total': total_value,
                'activo': getattr(cliente, 'activo', True)
            }
            
            # Añadir campos opcionales si existen
            if hasattr(cliente, 'razon_social') and cliente.razon_social:
                client_data['razon_social'] = cliente.razon_social
            else:
                client_data['razon_social'] = cliente.nombre
                
            if hasattr(cliente, 'fecha_creacion') and cliente.fecha_creacion:
                # Verificar si es un string o un objeto datetime
                if hasattr(cliente.fecha_creacion, 'isoformat'):
                    client_data['fecha_creacion'] = cliente.fecha_creacion.isoformat()
                else:
                    # Si es un string, intentar convertirlo a datetime
                    try:
                        from datetime import datetime
                        # Intentar parsear la fecha si es un string
                        if isinstance(cliente.fecha_creacion, str):
                            # Asumimos formato YYYY-MM-DD
                            client_data['fecha_creacion'] = cliente.fecha_creacion
                        else:
                            client_data['fecha_creacion'] = None
                    except (ValueError, AttributeError):
                        client_data['fecha_creacion'] = None
            else:
                client_data['fecha_creacion'] = None
                
            clients_data.append(client_data)
        
        # Ordenar por fecha de creación (más recientes primero)
        clients_data.sort(
            key=lambda x: x['fecha_creacion'] or '1900-01-01', 
            reverse=True
        )
        
        # Tomar solo los 10 primeros para la respuesta
        top_clients = clients_data[:10]
        
        return jsonify({
            'success': True,
            'data': {
                'clientes': top_clients,
                'estadisticas': {
                    'total_clientes': len(clientes),
                    'clientes_activos': len([c for c in clientes if getattr(c, 'activo', True)]),
                    'total_contratos': len(contratos),
                    'valor_total': sum(c['valor_total'] for c in clients_data)
                },
                'metadata': {
                    'total': len(top_clients),
                    'timestamp': datetime.now().isoformat()
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener resumen de clientes: {str(e)}'
        }), 500

# ===== RUTA API COMBINADA (MANTENIDA PARA COMPATIBILIDAD) =====

@clients_bp.route('/api/providers-clients-main', methods=['GET'])
@api_login_required
def api_get_providers_clients_main():
    """API combinada para obtener datos de proveedores y clientes para el dashboard principal"""
    try:
        from database.models import Proveedor
        
        # Obtener clientes
        clientes_db = Cliente.get_all()
        clientes = [c for c in clientes_db if c.tipo_cliente == 'cliente']
        
        # Obtener proveedores
        proveedores = Proveedor.get_all()
        
        # Obtener contratos
        contratos = Contrato.get_all()
        
        # Estadísticas de clientes
        total_clientes = len(clientes)
        clientes_activos = len([c for c in clientes if c.activo])
        contratos_clientes = [c for c in contratos if any(cl.id == c.cliente_id for cl in clientes)]
        valor_total_clientes = sum([c.monto_actual for c in contratos_clientes if c.estado == 'activo'])
        
        # Estadísticas de proveedores
        total_proveedores = len(proveedores)
        proveedores_activos = len([p for p in proveedores if p.activo])
        contratos_proveedores = [c for c in contratos if any(p.id == c.proveedor_id for p in proveedores) if hasattr(c, 'proveedor_id')]
        valor_total_proveedores = sum([c.monto_actual for c in contratos_proveedores if c.estado == 'activo'])
        
        estadisticas = {
            'clientes': {
                'total': total_clientes,
                'activos': clientes_activos,
                'contratos': len(contratos_clientes),
                'valor_total': int(valor_total_clientes)
            },
            'proveedores': {
                'total': total_proveedores,
                'activos': proveedores_activos,
                'contratos': len(contratos_proveedores),
                'valor_total': int(valor_total_proveedores)
            }
        }
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos principales: {str(e)}'
        }), 500