from flask import Flask, render_template, jsonify
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

# Ruta principal - Dashboard PACTA
@app.route('/')
def dashboard():
    contratos = generar_contratos_simulados()
    
    # Estadísticas generales
    total_contratos = len(contratos)
    contratos_activos = len([c for c in contratos if c['estado'] == 'Activo'])
    contratos_por_vencer = len([c for c in contratos if c['estado'] == 'Por Vencer'])
    contratos_vencidos = len([c for c in contratos if c['estado'] == 'Vencido'])
    
    # Contratos próximos a vencer (próximos 30 días)
    proximos_vencer = [c for c in contratos if c['estado'] == 'Por Vencer']
    proximos_vencer.sort(key=lambda x: x['dias_para_vencer'])
    
    # Valor total de contratos activos
    valor_total_activos = sum([c['valor'] for c in contratos if c['estado'] == 'Activo'])
    
    estadisticas = {
        'total_contratos': total_contratos,
        'contratos_activos': contratos_activos,
        'contratos_por_vencer': contratos_por_vencer,
        'contratos_vencidos': contratos_vencidos,
        'valor_total_activos': valor_total_activos,
        'proximos_vencer': proximos_vencer[:5]  # Solo los 5 más próximos
    }
    
    return render_template('dashboard.html', titulo='Dashboard PACTA', estadisticas=estadisticas)

# Ruta de ejemplo
@app.route('/about')
def about():
    return render_template('about.html', titulo='Acerca de')

# API para obtener datos de contratos
@app.route('/api/contratos')
def api_contratos():
    contratos = generar_contratos_simulados()
    return jsonify(contratos)

# API para estadísticas del dashboard
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