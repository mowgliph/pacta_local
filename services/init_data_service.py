from database.models import Usuario, Cliente, Contrato, PersonaResponsable, Suplemento, ActividadSistema, Notificacion
from datetime import datetime, timedelta
import random

class InitDataService:
    """Servicio para inicialización de datos de ejemplo en la base de datos"""
    
    def __init__(self):
        self.usuarios_creados = []
        self.clientes_creados = []
        self.contratos_creados = []
    
    def verificar_base_datos_vacia(self):
        """Verifica si la base de datos está vacía revisando todas las tablas principales"""
        try:
            usuarios_count = len(Usuario.get_all())
            clientes_count = len(Cliente.get_all())
            contratos_count = len(Contrato.get_all())
            
            return usuarios_count == 0 and clientes_count == 0 and contratos_count == 0
        except Exception as e:
            print(f"Error al verificar base de datos: {e}")
            return True  # Asumir vacía si hay error
    
    def verificar_usuario_admin_existe(self):
        """Verifica si existe un usuario administrador en el sistema"""
        try:
            usuarios = Usuario.get_all()
            for usuario in usuarios:
                if usuario.username == 'admin' and usuario.es_admin:
                    return True
            return False
        except Exception as e:
            print(f"Error al verificar usuario admin: {e}")
            return False
    
    def crear_usuario_admin_obligatorio(self):
        """Crea el usuario administrador obligatorio si no existe"""
        if not self.verificar_usuario_admin_existe():
            print("Creando usuario administrador obligatorio...")
            admin = Usuario(
                nombre='Administrador del Sistema',
                email='admin@empresa.com',
                username='admin',
                password='pacta',
                telefono='555-0100',
                cargo='Administrador del Sistema',
                departamento='TI',
                es_admin=True,
                rol='admin'
            )
            admin.save()
            print(f"Usuario administrador creado: username='admin', password='pacta'")
            return True
        else:
            print("Usuario administrador ya existe en el sistema.")
            return False
    
    def crear_usuarios_ejemplo(self):
        """Crea usuarios de ejemplo con diferentes roles"""
        print("Creando usuarios de ejemplo...")
        
        # Crear usuario administrador por defecto con credenciales específicas
        admin = Usuario(
            nombre='Administrador del Sistema',
            email='admin@empresa.com',
            username='admin',
            password='pacta',
            telefono='555-0100',
            cargo='Administrador del Sistema',
            departamento='TI',
            es_admin=True,
            rol='admin'
        )
        admin.save()
        self.usuarios_creados.append(admin)
        print(f"Usuario administrador creado: username='admin', password='pacta'")
        
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
            self.usuarios_creados.append(usuario)
    
    def crear_clientes_proveedores_ejemplo(self):
        """Crea clientes y proveedores de ejemplo"""
        print("Creando clientes y proveedores de ejemplo...")
        
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
            self.clientes_creados.append(cliente)
    
    def crear_personas_responsables(self):
        """Crea personas responsables para cada cliente/proveedor"""
        print("Creando personas responsables...")
        
        for cliente in self.clientes_creados:
            # Persona principal (ya definida en contacto_principal)
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
    
    def crear_contratos_ejemplo(self):
        """Crea contratos de ejemplo"""
        print("Creando contratos de ejemplo...")
        
        tipos_contrato = ['Servicios Profesionales', 'Suministro de Materiales', 'Mantenimiento Preventivo', 'Consultoría Especializada', 'Arrendamiento de Equipos', 'Desarrollo de Software', 'Capacitación', 'Outsourcing']
        estados_contrato = ['activo', 'borrador', 'suspendido', 'terminado']
        
        personas_responsables = PersonaResponsable.get_all()
        
        for i in range(1, 31):  # Crear 30 contratos de ejemplo
            cliente = random.choice(self.clientes_creados)
            usuario = random.choice(self.usuarios_creados)
            tipo = random.choice(tipos_contrato)
            estado = random.choice(estados_contrato)
            
            # Obtener persona responsable del cliente seleccionado
            personas_cliente = [p for p in personas_responsables if p.cliente_id == cliente.id]
            persona_responsable = random.choice(personas_cliente) if personas_cliente else None
            
            # Fechas realistas
            fecha_inicio = datetime.now().date() - timedelta(days=random.randint(30, 730))  # Hasta 2 años atrás
            duracion = random.randint(90, 1095)  # Entre 3 meses y 3 años
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
            self.contratos_creados.append(contrato)
    
    def crear_suplementos_ejemplo(self):
        """Crea suplementos para algunos contratos"""
        print("Creando suplementos de ejemplo...")
        
        contratos_con_suplementos = random.sample(self.contratos_creados, min(10, len(self.contratos_creados)))
        tipos_modificacion = ['Ampliación de Alcance', 'Modificación de Monto', 'Extensión de Plazo', 'Cambio de Especificaciones', 'Adición de Servicios']
        estados_suplemento = ['pendiente', 'aprobado', 'rechazado']
        
        for i, contrato in enumerate(contratos_con_suplementos, 1):
            num_suplementos = random.randint(1, 3)
            
            for j in range(num_suplementos):
                tipo_mod = random.choice(tipos_modificacion)
                estado_sup = random.choice(estados_suplemento)
                usuario_autoriza = random.choice(self.usuarios_creados)
                
                # Monto de modificación según el tipo
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
    
    def crear_notificaciones_ejemplo(self):
        """Crea notificaciones de ejemplo"""
        print("Creando notificaciones de ejemplo...")
        
        tipos_notificacion = ['system', 'contract_expiring', 'contract_expired', 'user', 'report']
        
        for usuario in self.usuarios_creados:
            num_notificaciones = random.randint(3, 8)
            
            for i in range(num_notificaciones):
                tipo_notif = random.choice(tipos_notificacion)
                is_read = random.choice([True, False])
                
                if tipo_notif == 'contract_expiring':
                    contrato_relacionado = random.choice(self.contratos_creados)
                    title = f'Contrato próximo a vencer: {contrato_relacionado.numero_contrato}'
                    message = f'El contrato {contrato_relacionado.numero_contrato} vence el {contrato_relacionado.fecha_fin}. Considere iniciar el proceso de renovación.'
                    contract_id = contrato_relacionado.id
                elif tipo_notif == 'contract_expired':
                    contrato_relacionado = random.choice(self.contratos_creados)
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
    
    def crear_actividades_sistema(self):
        """Crea actividades del sistema"""
        print("Creando actividades del sistema...")
        
        acciones = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'IMPORT']
        tablas = ['usuarios', 'clientes', 'contratos', 'suplementos', 'notificaciones']
        
        for i in range(50):  # 50 actividades de ejemplo
            usuario = random.choice(self.usuarios_creados)
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
    
    def crear_datos_ejemplo_completos(self):
        """Crea datos de ejemplo completos en la base de datos para todas las funcionalidades"""
        try:
            # SIEMPRE verificar y crear usuario administrador primero
            admin_creado = self.crear_usuario_admin_obligatorio()
            
            # Verificar si la base de datos está vacía para crear datos de ejemplo
            if self.verificar_base_datos_vacia():
                print("Base de datos vacía detectada. Creando datos de ejemplo completos...")
                # Crear datos en orden de dependencias
                self.crear_usuarios_ejemplo()
                self.crear_clientes_proveedores_ejemplo()
                self.crear_personas_responsables()
                self.crear_contratos_ejemplo()
                self.crear_suplementos_ejemplo()
                self.crear_notificaciones_ejemplo()
                self.crear_actividades_sistema()
                
                print("¡Datos de ejemplo creados exitosamente!")
                print(f"- {len(self.usuarios_creados)} usuarios creados")
                print(f"- {len(self.clientes_creados)} clientes/proveedores creados")
                print(f"- {len(self.contratos_creados)} contratos creados")
                print(f"- Suplementos, notificaciones y actividades del sistema incluidos")
                
                return {
                    'success': True,
                    'message': 'Datos de ejemplo creados exitosamente',
                    'admin_created': admin_creado,
                    'data': {
                        'usuarios': len(self.usuarios_creados),
                        'clientes': len(self.clientes_creados),
                        'contratos': len(self.contratos_creados)
                    }
                }
            else:
                print("Base de datos contiene datos existentes. Solo se verificó/creó usuario administrador.")
                return {
                    'success': True,
                    'message': 'Usuario administrador verificado/creado. Base de datos ya contiene datos.',
                    'admin_created': admin_creado,
                    'data': {
                        'usuarios': 0,
                        'clientes': 0,
                        'contratos': 0
                    }
                }
            
        except Exception as e:
            print(f"Error al crear datos de ejemplo: {e}")
            return {
                'success': False,
                'message': f'Error al crear datos de ejemplo: {str(e)}'
            }