from flask import Flask
from database import db_manager
from database.models import Usuario
from routes import register_blueprints
from services.backup_scheduler import start_backup_scheduler

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración para desarrollo
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'

# Configuración específica de Jinja2 para evitar problemas de recursión
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}
# Deshabilitar autoescape temporalmente para resolver recursión
app.jinja_env.autoescape = False

# Registrar blueprints
register_blueprints(app)

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
    from database.models import Cliente, Contrato
    from datetime import datetime, timedelta
    import random
    
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
    estados = ['activo', 'pendiente', 'vencido', 'renovado']
    
    clientes_db = Cliente.get_all()
    usuarios_db = Usuario.get_all()
    
    for i in range(1, 21):  # Crear 20 contratos de ejemplo
        cliente = random.choice(clientes_db)
        usuario = random.choice(usuarios_db)
        tipo = random.choice(tipos_contrato)
        estado = random.choice(estados)
        
        # Fechas aleatorias
        fecha_inicio = datetime.now().date() - timedelta(days=random.randint(30, 365))
        duracion = random.randint(180, 1095)  # Entre 6 meses y 3 años
        fecha_fin = fecha_inicio + timedelta(days=duracion)
        
        # Montos aleatorios
        monto_original = random.randint(50000, 5000000)
        monto_actual = monto_original + random.randint(-10000, 100000)
        
        contrato = Contrato(
            numero_contrato=f'CONT-{i:04d}',
            titulo=f'Contrato de {tipo} - {cliente.nombre}',
            descripcion=f'Contrato para {tipo.lower()} con {cliente.nombre}',
            tipo_contrato=tipo,
            cliente_id=cliente.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            monto_original=monto_original,
            monto_actual=monto_actual,
            estado=estado,
            usuario_responsable_id=usuario.id
        )
        contrato.save()

if __name__ == '__main__':
    # Inicializar el scheduler de backups
    backup_scheduler = start_backup_scheduler()
    
    try:
        # Ejecutar la aplicación en modo desarrollo
        app.run(host='127.0.0.1', port=5000, debug=True)
    finally:
        # Asegurar que el scheduler se detenga al cerrar la aplicación
        if 'backup_scheduler' in locals():
            backup_scheduler.shutdown()