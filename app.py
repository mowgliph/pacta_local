from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import random

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración para desarrollo
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'

# Datos simulados para contratos
def generar_contratos_simulados():
    contratos = []
    tipos_contrato = ['Servicios', 'Suministro', 'Mantenimiento', 'Consultoría', 'Arrendamiento']
    estados = ['Activo', 'Por Vencer', 'Vencido', 'En Renovación']
    
    for i in range(1, 51):  # 50 contratos simulados
        fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 365))
        duracion = random.randint(90, 730)  # Entre 3 meses y 2 años
        fecha_vencimiento = fecha_inicio + timedelta(days=duracion)
        
        # Determinar estado basado en fecha de vencimiento
        dias_para_vencer = (fecha_vencimiento - datetime.now()).days
        if dias_para_vencer < 0:
            estado = 'Vencido'
        elif dias_para_vencer <= 30:
            estado = 'Por Vencer'
        else:
            estado = 'Activo'
            
        contrato = {
            'id': f'CONT-{i:03d}',
            'nombre': f'Contrato {tipos_contrato[random.randint(0, len(tipos_contrato)-1)]} {i}',
            'tipo': tipos_contrato[random.randint(0, len(tipos_contrato)-1)],
            'proveedor': f'Proveedor {chr(65 + (i % 26))}',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_vencimiento': fecha_vencimiento.strftime('%Y-%m-%d'),
            'valor': random.randint(10000, 500000),
            'estado': estado,
            'dias_para_vencer': dias_para_vencer
        }
        contratos.append(contrato)
    
    return contratos

# Ruta principal - Redirigir a dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Ruta del Dashboard Principal
@app.route('/dashboard')
def dashboard():
    contratos = generar_contratos_simulados()
    
    # Calcular métricas generales del sistema
    total_contratos = len(contratos)
    contratos_activos = len([c for c in contratos if c['estado'] == 'Activo'])
    contratos_por_vencer = len([c for c in contratos if c['estado'] == 'Por Vencer'])
    valor_total = sum([c['valor'] for c in contratos])
    
    # Métricas de reportes simuladas
    total_reportes = 89
    reportes_mes = 23
    reportes_pendientes = 5
    
    # Métricas de usuarios simuladas
    usuarios_activos = 12
    sesiones_mes = 156
    
    # Métricas de rendimiento simuladas
    uptime = 99.8
    tiempo_respuesta = 245  # ms
    
    estadisticas = {
        'total_contratos': total_contratos,
        'contratos_activos': contratos_activos,
        'contratos_por_vencer': contratos_por_vencer,
        'valor_total': f'{valor_total/1000000:.1f}M',
        'total_reportes': total_reportes,
        'reportes_mes': reportes_mes,
        'reportes_pendientes': reportes_pendientes,
        'usuarios_activos': usuarios_activos,
        'sesiones_mes': sesiones_mes,
        'uptime': uptime,
        'tiempo_respuesta': tiempo_respuesta
    }
    
    return render_template('dashboard.html', estadisticas=estadisticas, contratos=contratos[:5])

@app.route('/contratos')
def contratos():
    contratos_data = generar_contratos_simulados()
    
    # Calcular estadísticas para la página de contratos
    total_contratos = len(contratos_data)
    contratos_activos = len([c for c in contratos_data if c['estado'] == 'Activo'])
    proximos_vencer = len([c for c in contratos_data if c['estado'] == 'Por Vencer'])
    valor_total = sum([c['valor'] for c in contratos_data])
    
    estadisticas = {
        'total_contratos': total_contratos,
        'contratos_activos': contratos_activos,
        'proximos_vencer': proximos_vencer,
        'valor_total': f'{valor_total/1000000:.1f}M'
    }
    
    return render_template('contratos.html', 
                         contratos=contratos_data, 
                         estadisticas=estadisticas)

@app.route('/reportes')
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
    
    return render_template('reportes.html', 
                         reportes=reportes_data, 
                         estadisticas=estadisticas)

@app.route('/configuracion')
def configuracion():
    # Generar estadísticas para la página de configuración
    estadisticas = {
        'usuarios_activos': 24,
        'configuraciones': 12,
        'ultimo_backup': 'Ayer',
        'espacio_usado': '68%'
    }
    
    return render_template('configuracion.html', estadisticas=estadisticas)

@app.route('/usuario')
def usuario():
    # Datos del usuario (normalmente vendrían de la base de datos)
    usuario_data = {
        'nombre': 'Ana Martínez',
        'cargo': 'Gerente de Operaciones',
        'email': 'ana.martinez@pacta.com',
        'telefono': '+57 300 123 4567',
        'dias_activo': 245,
        'nivel_acceso': 'Admin',
        'contratos_creados': 45,
        'reportes_generados': 23,
        'ultimo_acceso': 'Hoy 09:30',
        'sesiones_mes': 28
    }
    
    # Estadísticas generales (reutilizadas)
    estadisticas = {
        'contratos_activos': 156,
        'valor_total': '2.4M',
        'proximos_vencer': 23,
        'reportes_generados': 89
    }
    
    return render_template('usuario.html', usuario=usuario_data, estadisticas=estadisticas)

# API para obtener datos de contratos
@app.route('/api/contratos')
def api_contratos():
    contratos = generar_contratos_simulados()
    return jsonify(contratos)

# API para estadísticas generales
@app.route('/api/estadisticas')
def api_estadisticas():
    contratos = generar_contratos_simulados()
    
    # Agrupar por tipo de contrato
    tipos_count = {}
    for contrato in contratos:
        tipo = contrato['tipo']
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    # Agrupar por estado
    estados_count = {}
    for contrato in contratos:
        estado = contrato['estado']
        estados_count[estado] = estados_count.get(estado, 0) + 1
    
    return jsonify({
        'tipos_contrato': tipos_count,
        'estados_contrato': estados_count
    })

if __name__ == '__main__':
    # Ejecutar la aplicación en modo desarrollo
    app.run(host='127.0.0.1', port=5000, debug=True)