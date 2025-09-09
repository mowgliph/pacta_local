from flask import Blueprint, jsonify, request
from database.database import db_manager
from database.models import Usuario, Cliente, Contrato
from datetime import datetime, timedelta
import random

init_data_api = Blueprint('init_data_api', __name__)

def verificar_base_datos_vacia():
    """Verifica si la base de datos está vacía revisando las tablas principales"""
    try:
        # Verificar usuarios
        usuarios = Usuario.get_all()
        if usuarios and len(usuarios) > 0:
            return False
            
        # Verificar clientes
        clientes = Cliente.get_all()
        if clientes and len(clientes) > 0:
            return False
            
        # Verificar contratos
        contratos = Contrato.get_all()
        if contratos and len(contratos) > 0:
            return False
            
        # Si todas las tablas principales están vacías, la BD está vacía
        return True
        
    except Exception as e:
        print(f"Error al verificar base de datos: {e}")
        return True  # Asumir vacía si hay error

def crear_datos_ejemplo_completos():
    """Crea datos de ejemplo completos en la base de datos para todas las funcionalidades"""
    from database.models import PersonaResponsable, Suplemento, ActividadSistema, Notificacion
    
    try:
        # Crear usuario administrador por defecto
        admin = Usuario(
            nombre='Administrador del Sistema',
            email='admin@empresa.com',
            username='admin',
            password='admin123',
            telefono='555-0100',
            cargo='Administrador del Sistema',
            departamento='TI',
            es_admin=True,
            rol='admin'
        )
        admin.save()
        
        # Crear usuarios de ejemplo con diferentes roles
        usuarios_ejemplo = [
            Usuario(nombre='Juan Pérez Martínez', email='juan.perez@empresa.com', username='juan.perez', password='123456', telefono='555-0101', cargo='Gerente de Contratos', departamento='Legal', rol='user'),
            Usuario(nombre='María García López', email='maria.garcia@empresa.com', username='maria.garcia', password='123456', telefono='555-0102', cargo='Analista de Contratos', departamento='Compras', rol='user'),
            Usuario(nombre='Carlos López Hernández', email='carlos.lopez@empresa.com', username='carlos.lopez', password='123456', telefono='555-0103', cargo='Director de Operaciones', departamento='Operaciones', rol='user'),
            Usuario(nombre='Ana Rodríguez Silva', email='ana.rodriguez@empresa.com', username='ana.rodriguez', password='123456', telefono='555-0104', cargo='Supervisora de Contratos', departamento='Legal', rol='user'),
            Usuario(nombre='Roberto Martín Torres', email='roberto.martin@empresa.com', username='roberto.martin', password='123456', telefono='555-0105', cargo='Coordinador de Proveedores', departamento='Compras', rol='viewer')
        ]
        
        for usuario in usuarios_ejemplo:
            usuario.save()
        
        # Crear clientes de ejemplo
        clientes_ejemplo = [
            Cliente(nombre='Empresa ABC S.A.', tipo_cliente='cliente', rfc='ABC123456789', direccion='Av. Principal 123, Col. Centro', telefono='555-0001', email='contacto@abc.com', contacto_principal='Ana Martínez'),
            Cliente(nombre='Corporativo XYZ', tipo_cliente='cliente', rfc='XYZ987654321', direccion='Calle Secundaria 456, Col. Industrial', telefono='555-0002', email='info@xyz.com', contacto_principal='Roberto Silva'),
            Cliente(nombre='Grupo Empresarial Delta', tipo_cliente='cliente', rfc='DEL456123789', direccion='Blvd. Empresarial 789, Col. Moderna', telefono='555-0010', email='ventas@delta.com', contacto_principal='Carmen Vega'),
            Cliente(nombre='Industrias Gamma S.A. de C.V.', tipo_cliente='cliente', rfc='GAM789456123', direccion='Zona Industrial Norte 321', telefono='555-0011', email='contratos@gamma.com', contacto_principal='Luis Morales')
        ]
        
        # Crear proveedores de ejemplo
        proveedores_ejemplo = [
            Cliente(nombre='Tech Solutions Provider', tipo_cliente='proveedor', rfc='TEC456789123', direccion='Zona Tecnológica 789, Col. Innovación', telefono='555-0003', email='ventas@techsol.com', contacto_principal='Laura Rodríguez'),
            Cliente(nombre='Servicios Integrales SA', tipo_cliente='proveedor', rfc='SIN789123456', direccion='Centro Comercial 321, Col. Servicios', telefono='555-0004', email='servicios@integrales.com', contacto_principal='Miguel Torres'),
            Cliente(nombre='Constructora Beta Ltda.', tipo_cliente='proveedor', rfc='BET321654987', direccion='Av. Construcción 654, Col. Obras', telefono='555-0012', email='proyectos@beta.com', contacto_principal='Patricia Jiménez'),
            Cliente(nombre='Suministros Alpha Corp.', tipo_cliente='proveedor', rfc='ALP987321654', direccion='Parque Industrial 987, Col. Suministros', telefono='555-0013', email='ventas@alpha.com', contacto_principal='Fernando Castro')
        ]
        
        todos_clientes = clientes_ejemplo + proveedores_ejemplo
        for cliente in todos_clientes:
            cliente.save()
        
        # Crear personas responsables para cada cliente/proveedor
        clientes_db = Cliente.get_all()
        for cliente in clientes_db:
            # Persona principal
            persona_principal = PersonaResponsable(
                cliente_id=cliente.id,
                nombre=cliente.contacto_principal,
                cargo='Gerente de Cuenta' if cliente.tipo_cliente == 'cliente' else 'Representante de Ventas',
                telefono=cliente.telefono,
                email=cliente.email,
                es_principal=True
            )
            persona_principal.save()
            
            # Persona secundaria
            nombres_secundarios = ['José González', 'Elena Vargas', 'David Ruiz', 'Sandra Moreno', 'Alberto Díaz']
            persona_secundaria = PersonaResponsable(
                cliente_id=cliente.id,
                nombre=random.choice(nombres_secundarios),
                cargo='Asistente Administrativo',
                telefono=f'555-{random.randint(1000, 9999)}',
                email=f'asistente{cliente.id}@{cliente.email.split("@")[1]}',
                es_principal=False
            )
            persona_secundaria.save()
        
        # Crear contratos de ejemplo
        tipos_contrato = ['Servicios Profesionales', 'Suministro de Materiales', 'Mantenimiento Preventivo', 'Consultoría Especializada', 'Arrendamiento de Equipos', 'Desarrollo de Software', 'Capacitación', 'Outsourcing']
        estados_contrato = ['activo', 'borrador', 'suspendido', 'terminado']
        
        usuarios_db = Usuario.get_all()
        personas_responsables = PersonaResponsable.get_all()
        
        contratos_creados = []
        for i in range(1, 31):  # Crear 30 contratos de ejemplo
            cliente = random.choice(clientes_db)
            usuario = random.choice(usuarios_db)
            tipo = random.choice(tipos_contrato)
            estado = random.choice(estados_contrato)
            
            # Obtener persona responsable del cliente seleccionado
            personas_cliente = [p for p in personas_responsables if p.cliente_id == cliente.id]
            persona_responsable = random.choice(personas_cliente) if personas_cliente else None
            
            # Fechas realistas
            fecha_inicio = datetime.now().date() - timedelta(days=random.randint(30, 730))
            duracion = random.randint(90, 1095)
            fecha_fin = fecha_inicio + timedelta(days=duracion)
            
            # Montos realistas según el tipo
            base_amounts = {
                'Servicios Profesionales': (100000, 2000000),
                'Suministro de Materiales': (50000, 5000000),
                'Mantenimiento Preventivo': (80000, 800000),
                'Consultoría Especializada': (150000, 3000000),
                'Arrendamiento de Equipos': (30000, 1500000),
                'Desarrollo de Software': (200000, 5000000),
                'Capacitación': (25000, 500000),
                'Outsourcing': (300000, 10000000)
            }
            
            min_amount, max_amount = base_amounts.get(tipo, (50000, 1000000))
            monto_original = random.randint(min_amount, max_amount)
            monto_actual = monto_original + random.randint(-int(monto_original*0.1), int(monto_original*0.2))
            
            contrato = Contrato(
                numero_contrato=f'CONT-{datetime.now().year}-{i:04d}',
                titulo=f'{tipo} - {cliente.nombre}',
                descripcion=f'Contrato para {tipo.lower()} con {cliente.nombre}. Incluye servicios especializados y soporte técnico según especificaciones técnicas acordadas.',
                tipo_contrato=tipo,
                cliente_id=cliente.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                monto_original=monto_original,
                monto_actual=monto_actual,
                estado=estado,
                usuario_responsable_id=usuario.id,
                persona_responsable_id=persona_responsable.id if persona_responsable else None
            )
            contrato.save()
            contratos_creados.append(contrato)
        
        # Crear suplementos para algunos contratos
        contratos_con_suplementos = random.sample(contratos_creados, min(10, len(contratos_creados)))
        tipos_modificacion = ['Ampliación de Alcance', 'Modificación de Monto', 'Extensión de Plazo', 'Cambio de Especificaciones', 'Adición de Servicios']
        estados_suplemento = ['pendiente', 'aprobado', 'rechazado']
        
        for i, contrato in enumerate(contratos_con_suplementos, 1):
            num_suplementos = random.randint(1, 3)
            
            for j in range(num_suplementos):
                tipo_mod = random.choice(tipos_modificacion)
                estado_sup = random.choice(estados_suplemento)
                usuario_autoriza = random.choice(usuarios_db)
                
                if 'Monto' in tipo_mod:
                    monto_mod = random.randint(10000, int(contrato.monto_original * 0.3))
                elif 'Ampliación' in tipo_mod or 'Adición' in tipo_mod:
                    monto_mod = random.randint(50000, int(contrato.monto_original * 0.5))
                else:
                    monto_mod = 0
                
                suplemento = Suplemento(
                    contrato_id=contrato.id,
                    numero_suplemento=f'SUP-{contrato.numero_contrato}-{j+1:02d}',
                    tipo_modificacion=tipo_mod,
                    descripcion=f'{tipo_mod} para el contrato {contrato.numero_contrato}. Modificación solicitada por cambios en los requerimientos del proyecto.',
                    monto_modificacion=monto_mod,
                    fecha_modificacion=contrato.fecha_inicio + timedelta(days=random.randint(30, 300)),
                    usuario_autoriza_id=usuario_autoriza.id,
                    estado=estado_sup
                )
                suplemento.save()
        
        # Crear notificaciones de ejemplo
        tipos_notificacion = ['system', 'contract_expiring', 'contract_expired', 'user', 'report']
        
        for usuario in usuarios_db:
            num_notificaciones = random.randint(3, 8)
            
            for i in range(num_notificaciones):
                tipo_notif = random.choice(tipos_notificacion)
                is_read = random.choice([True, False])
                
                if tipo_notif == 'contract_expiring':
                    contrato_relacionado = random.choice(contratos_creados)
                    title = f'Contrato próximo a vencer: {contrato_relacionado.numero_contrato}'
                    message = f'El contrato {contrato_relacionado.numero_contrato} vence el {contrato_relacionado.fecha_fin}. Considere iniciar el proceso de renovación.'
                    contract_id = contrato_relacionado.id
                elif tipo_notif == 'contract_expired':
                    contrato_relacionado = random.choice(contratos_creados)
                    title = f'Contrato vencido: {contrato_relacionado.numero_contrato}'
                    message = f'El contrato {contrato_relacionado.numero_contrato} ha vencido. Requiere atención inmediata.'
                    contract_id = contrato_relacionado.id
                elif tipo_notif == 'system':
                    title = 'Actualización del sistema'
                    message = 'El sistema ha sido actualizado con nuevas funcionalidades. Revise las novedades en el panel de control.'
                    contract_id = None
                elif tipo_notif == 'user':
                    title = 'Bienvenido al sistema PACTA'
                    message = f'Bienvenido {usuario.nombre}. Su cuenta ha sido configurada correctamente.'
                    contract_id = None
                else:  # report
                    title = 'Reporte mensual disponible'
                    message = 'El reporte mensual de contratos está disponible para descarga en la sección de reportes.'
                    contract_id = None
                
                notificacion = Notificacion(
                    usuario_id=usuario.id,
                    title=title,
                    message=message,
                    type=tipo_notif,
                    is_read=is_read,
                    contract_id=contract_id
                )
                notificacion.save()
        
        # Crear actividades del sistema
        acciones = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'IMPORT']
        tablas = ['usuarios', 'clientes', 'contratos', 'suplementos', 'notificaciones']
        
        for i in range(50):
            usuario = random.choice(usuarios_db)
            accion = random.choice(acciones)
            tabla = random.choice(tablas)
            
            actividad = ActividadSistema(
                usuario_id=usuario.id,
                accion=accion,
                tabla_afectada=tabla,
                registro_id=random.randint(1, 100),
                detalles=f'Usuario {usuario.nombre} realizó {accion} en {tabla}'
            )
            actividad.save()
        
        return {
            'usuarios': len(usuarios_db),
            'clientes': len(clientes_db),
            'contratos': len(contratos_creados),
            'suplementos': len(contratos_con_suplementos) * 2,  # Aproximado
            'notificaciones': len(usuarios_db) * 5,  # Aproximado
            'actividades': 50
        }
        
    except Exception as e:
        print(f"Error creando datos de ejemplo: {e}")
        raise e

@init_data_api.route('/api/check-database-empty', methods=['GET'])
def check_database_empty():
    """API endpoint para verificar si la base de datos está vacía y si existe usuario administrador"""
    try:
        from services.init_data_service import InitDataService
        init_service = InitDataService()
        is_empty = init_service.verificar_base_datos_vacia()
        admin_exists = init_service.verificar_usuario_admin_existe()
        
        return jsonify({
            'success': True,
            'is_empty': is_empty,
            'admin_exists': admin_exists,
            'needs_initialization': is_empty or not admin_exists
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@init_data_api.route('/api/initialize-sample-data', methods=['POST'])
def initialize_sample_data():
    """API endpoint para inicializar datos de ejemplo"""
    try:
        # Verificar que la base de datos esté vacía antes de crear datos
        if not verificar_base_datos_vacia():
            return jsonify({
                'success': False,
                'message': 'La base de datos ya contiene datos. No se pueden crear datos de ejemplo.'
            }), 400
        
        # Crear datos de ejemplo
        summary = crear_datos_ejemplo_completos()
        
        return jsonify({
            'success': True,
            'message': 'Datos de ejemplo creados exitosamente',
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear datos de ejemplo: {str(e)}'
        }), 500

@init_data_api.route('/api/create-admin-user', methods=['POST'])
def create_admin_user():
    """Crea únicamente el usuario administrador"""
    try:
        from services.init_data_service import InitDataService
        init_service = InitDataService()
        
        # Verificar si ya existe
        if init_service.verificar_usuario_admin_existe():
            return jsonify({
                'success': True,
                'message': 'El usuario administrador ya existe'
            })
        
        # Crear usuario admin
        admin_created = init_service.crear_usuario_admin_obligatorio()
        
        if admin_created:
            return jsonify({
                'success': True,
                'message': 'Usuario administrador creado exitosamente con contraseña "pacta"'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No se pudo crear el usuario administrador'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear usuario administrador: {str(e)}'
        }), 500