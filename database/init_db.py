#!/usr/bin/env python3
"""
Script para inicializar la base de datos SQLite con datos de ejemplo.
Ejecuta este script para crear la base de datos y poblarla con datos de prueba.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Agregar los directorios necesarios al path para importar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Importar los módulos
from database import db_manager
from models import Usuario, Cliente, Contrato, Suplemento, ActividadSistema

def limpiar_base_datos():
    """Elimina la base de datos existente para empezar desde cero"""
    if os.path.exists('pacta_local.db'):
        os.remove('pacta_local.db')
        print("Base de datos anterior eliminada.")

def crear_usuarios_ejemplo():
    """Crea usuarios de ejemplo"""
    print("Creando usuarios de ejemplo...")
    
    usuarios = [
        Usuario(
            nombre='Juan Pérez Martínez',
            email='juan.perez@empresa.com',
            telefono='555-0101',
            cargo='Gerente de Contratos',
            departamento='Legal'
        ),
        Usuario(
            nombre='María García López',
            email='maria.garcia@empresa.com',
            telefono='555-0102',
            cargo='Analista de Contratos',
            departamento='Compras'
        ),
        Usuario(
            nombre='Carlos López Rodríguez',
            email='carlos.lopez@empresa.com',
            telefono='555-0103',
            cargo='Director de Operaciones',
            departamento='Operaciones'
        ),
        Usuario(
            nombre='Ana Martínez Silva',
            email='ana.martinez@empresa.com',
            telefono='555-0104',
            cargo='Coordinadora de Proyectos',
            departamento='Proyectos'
        ),
        Usuario(
            nombre='Roberto Silva Torres',
            email='roberto.silva@empresa.com',
            telefono='555-0105',
            cargo='Especialista en Compras',
            departamento='Compras'
        )
    ]
    
    for usuario in usuarios:
        usuario.save()
        print(f"  - Usuario creado: {usuario.nombre}")
    
    return len(usuarios)

def crear_clientes_proveedores():
    """Crea clientes y proveedores de ejemplo"""
    print("Creando clientes y proveedores de ejemplo...")
    
    entidades = [
        # Clientes
        Cliente(
            nombre='Empresa ABC S.A. de C.V.',
            tipo_cliente='cliente',
            rfc='ABC123456789',
            direccion='Av. Principal 123, Col. Centro, Ciudad de México',
            telefono='555-1001',
            email='contacto@abc.com.mx',
            contacto_principal='Ana Martínez Directora'
        ),
        Cliente(
            nombre='Corporativo XYZ Internacional',
            tipo_cliente='cliente',
            rfc='XYZ987654321',
            direccion='Calle Secundaria 456, Col. Polanco, Ciudad de México',
            telefono='555-1002',
            email='info@xyz-internacional.com',
            contacto_principal='Roberto Silva Gerente'
        ),
        Cliente(
            nombre='Industrias DEF S.A.',
            tipo_cliente='cliente',
            rfc='DEF456789123',
            direccion='Blvd. Industrial 789, Zona Industrial, Monterrey',
            telefono='555-1003',
            email='ventas@industriasdef.com',
            contacto_principal='Laura Rodríguez Coordinadora'
        ),
        
        # Proveedores
        Cliente(
            nombre='Tech Solutions México S.A.',
            tipo_cliente='proveedor',
            rfc='TEC456789123',
            direccion='Zona Tecnológica 789, Col. Santa Fe, Ciudad de México',
            telefono='555-2001',
            email='ventas@techsolutions.mx',
            contacto_principal='Miguel Torres CTO'
        ),
        Cliente(
            nombre='Servicios Integrales del Norte',
            tipo_cliente='proveedor',
            rfc='SIN789123456',
            direccion='Centro Comercial 321, Col. Residencial, Guadalajara',
            telefono='555-2002',
            email='servicios@integrales-norte.com',
            contacto_principal='Patricia Hernández Directora'
        ),
        Cliente(
            nombre='Constructora Moderna S.A.',
            tipo_cliente='proveedor',
            rfc='CON321654987',
            direccion='Av. Construcción 654, Col. Industrial, Puebla',
            telefono='555-2003',
            email='proyectos@constructora-moderna.com',
            contacto_principal='Fernando Jiménez Ingeniero'
        ),
        Cliente(
            nombre='Suministros Empresariales Plus',
            tipo_cliente='proveedor',
            rfc='SUE147258369',
            direccion='Parque Industrial 147, Col. Logística, Tijuana',
            telefono='555-2004',
            email='suministros@empresariales-plus.com',
            contacto_principal='Gabriela Morales Gerente'
        )
    ]
    
    for entidad in entidades:
        entidad.save()
        print(f"  - {entidad.tipo_cliente.title()} creado: {entidad.nombre}")
    
    return len(entidades)

def crear_contratos_ejemplo():
    """Crea contratos de ejemplo con datos realistas"""
    print("Creando contratos de ejemplo...")
    
    tipos_contrato = [
        'Servicios de Consultoría',
        'Suministro de Materiales',
        'Mantenimiento de Equipos',
        'Desarrollo de Software',
        'Arrendamiento de Espacios',
        'Servicios de Limpieza',
        'Seguridad y Vigilancia',
        'Servicios de Catering',
        'Transporte y Logística',
        'Capacitación y Entrenamiento'
    ]
    
    estados = ['activo', 'borrador', 'suspendido', 'terminado']
    
    # Obtener IDs de clientes y usuarios
    clientes = Cliente.get_by_tipo('cliente') + Cliente.get_by_tipo('proveedor')
    usuarios = Usuario.get_all()
    
    contratos_creados = 0
    
    for i in range(1, 31):  # 30 contratos de ejemplo
        fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 730))
        duracion = random.randint(90, 1095)  # Entre 3 meses y 3 años
        fecha_fin = fecha_inicio + timedelta(days=duracion)
        
        tipo_seleccionado = tipos_contrato[random.randint(0, len(tipos_contrato)-1)]
        cliente_seleccionado = clientes[random.randint(0, len(clientes)-1)]
        usuario_seleccionado = usuarios[random.randint(0, len(usuarios)-1)]
        
        monto_base = random.randint(100000, 2000000)
        variacion = random.uniform(0.8, 1.2)  # Variación del 20%
        monto_actual = int(monto_base * variacion)
        
        contrato = Contrato(
            numero_contrato=f'CONT-{i:04d}',
            cliente_id=cliente_seleccionado.id,
            usuario_responsable_id=usuario_seleccionado.id,
            titulo=f'{tipo_seleccionado} - {cliente_seleccionado.nombre}',
            descripcion=f'Contrato para {tipo_seleccionado.lower()} con {cliente_seleccionado.nombre}. '
                       f'Incluye servicios especializados y entregables específicos según '
                       f'los términos y condiciones establecidos en el anexo técnico.',
            monto_original=monto_base,
            monto_actual=monto_actual,
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            estado=estados[random.randint(0, len(estados)-1)],
            tipo_contrato=tipo_seleccionado
        )
        contrato.save()
        contratos_creados += 1
        
        print(f"  - Contrato creado: {contrato.numero_contrato} - {contrato.titulo[:50]}...")
        
        # Crear suplementos para algunos contratos (30% de probabilidad)
        if random.random() < 0.3:
            crear_suplementos_para_contrato(contrato, usuarios)
    
    return contratos_creados

def crear_suplementos_para_contrato(contrato, usuarios):
    """Crea suplementos para un contrato específico"""
    tipos_modificacion = [
        'Ampliación de monto',
        'Extensión de plazo',
        'Modificación de alcance',
        'Cambio de especificaciones',
        'Ajuste de precios'
    ]
    
    num_suplementos = random.randint(1, 3)
    
    for i in range(num_suplementos):
        tipo_mod = tipos_modificacion[random.randint(0, len(tipos_modificacion)-1)]
        usuario_autoriza = usuarios[random.randint(0, len(usuarios)-1)]
        
        # Calcular monto de modificación basado en el tipo
        if 'monto' in tipo_mod.lower():
            monto_mod = random.randint(50000, 300000)
        elif 'precio' in tipo_mod.lower():
            monto_mod = random.randint(-100000, 200000)  # Puede ser negativo
        else:
            monto_mod = random.randint(0, 100000)
        
        suplemento = Suplemento(
            contrato_id=contrato.id,
            numero_suplemento=f'SUP-{contrato.numero_contrato}-{i+1:03d}',
            tipo_modificacion=tipo_mod,
            descripcion=f'Suplemento para {tipo_mod.lower()} del contrato {contrato.numero_contrato}. '
                       f'Modificación aprobada según solicitud del área usuaria.',
            monto_modificacion=monto_mod,
            fecha_modificacion=datetime.now().date(),
            usuario_autoriza_id=usuario_autoriza.id,
            estado='aprobado' if random.random() < 0.8 else 'pendiente'
        )
        suplemento.save()
        print(f"    - Suplemento creado: {suplemento.numero_suplemento}")

def crear_actividad_sistema():
    """Crea registros de actividad del sistema"""
    print("Creando registros de actividad del sistema...")
    
    usuarios = Usuario.get_all()
    acciones = [
        'Creó nuevo contrato',
        'Actualizó información de contrato',
        'Aprobó suplemento',
        'Generó reporte mensual',
        'Renovó contrato',
        'Modificó datos de cliente',
        'Creó nuevo usuario',
        'Actualizó configuración del sistema',
        'Exportó datos de contratos',
        'Realizó backup de base de datos'
    ]
    
    # Crear actividades de los últimos 30 días
    for i in range(50):
        usuario = usuarios[random.randint(0, len(usuarios)-1)]
        accion = acciones[random.randint(0, len(acciones)-1)]
        
        actividad = ActividadSistema(
            usuario_id=usuario.id,
            accion=accion,
            tabla_afectada='contratos' if 'contrato' in accion.lower() else 'sistema',
            registro_id=random.randint(1, 30) if 'contrato' in accion.lower() else None,
            detalles=f'Actividad realizada por {usuario.nombre}: {accion}'
        )
        actividad.save()
    
    # Actividad inicial del sistema
    actividad_inicial = ActividadSistema(
        usuario_id=usuarios[0].id,
        accion='Inicialización del sistema',
        tabla_afectada='sistema',
        detalles='Sistema inicializado con datos de ejemplo'
    )
    actividad_inicial.save()
    
    print(f"  - Creados 51 registros de actividad del sistema")

def mostrar_estadisticas():
    """Muestra estadísticas de la base de datos creada"""
    print("\n" + "="*50)
    print("ESTADÍSTICAS DE LA BASE DE DATOS")
    print("="*50)
    
    usuarios = Usuario.get_all()
    clientes = Cliente.get_by_tipo('cliente')
    proveedores = Cliente.get_by_tipo('proveedor')
    contratos = Contrato.get_all()
    contratos_activos = Contrato.get_all('activo')
    
    print(f"Usuarios creados: {len(usuarios)}")
    print(f"Clientes creados: {len(clientes)}")
    print(f"Proveedores creados: {len(proveedores)}")
    print(f"Contratos totales: {len(contratos)}")
    print(f"Contratos activos: {len(contratos_activos)}")
    
    # Calcular valor total de contratos activos
    valor_total = sum([c.monto_actual for c in contratos_activos])
    print(f"Valor total de contratos activos: ${valor_total:,.2f}")
    
    # Mostrar algunos ejemplos
    print("\nEjemplos de contratos creados:")
    for contrato in contratos[:5]:
        cliente = Cliente.get_by_id(contrato.cliente_id)
        print(f"  - {contrato.numero_contrato}: {contrato.titulo[:40]}... (${contrato.monto_actual:,.2f})")
    
    print("\n¡Base de datos inicializada correctamente!")
    print("Puedes ejecutar 'python app.py' para iniciar la aplicación.")

def main():
    """Función principal para inicializar la base de datos"""
    print("Inicializando base de datos SQLite para PACTA Local...")
    print("="*60)
    
    # Preguntar si se desea limpiar la base de datos existente
    if os.path.exists('pacta_local.db'):
        respuesta = input("¿Deseas eliminar la base de datos existente? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_base_datos()
    
    try:
        # Forzar la inicialización de la base de datos
        db_manager.init_database()
        print("Base de datos SQLite inicializada.")
        
        # Crear datos de ejemplo
        usuarios_creados = crear_usuarios_ejemplo()
        entidades_creadas = crear_clientes_proveedores()
        contratos_creados = crear_contratos_ejemplo()
        crear_actividad_sistema()
        
        # Mostrar estadísticas finales
        mostrar_estadisticas()
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())