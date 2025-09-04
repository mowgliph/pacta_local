from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from functools import wraps
from werkzeug.utils import secure_filename
from database.models import Contrato, Cliente, PersonaResponsable, DocumentoContrato, Suplemento
from datetime import datetime
import os

# Decorador para requerir login (simplificado)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

contratos_bp = Blueprint('contratos', __name__, url_prefix='/contratos')

# Configuración para subida de archivos
UPLOAD_FOLDER = 'uploads/contratos'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contratos_bp.route('/')
@login_required
def listar():
    """Lista todos los contratos con filtros"""
    # Obtener parámetros de filtro
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')
    search = request.args.get('search', '').strip()
    
    # Aplicar filtros
    if search:
        contratos = Contrato.search(search, cliente_id=cliente_id, estado=estado)
    elif cliente_id:
        contratos = Contrato.get_by_cliente(cliente_id, estado=estado)
    else:
        contratos = Contrato.get_all(estado=estado)
    
    # Obtener datos adicionales para cada contrato
    contratos_data = []
    for contrato in contratos:
        cliente = contrato.get_cliente()
        persona_responsable = contrato.get_persona_responsable()
        contratos_data.append({
            'contrato': contrato,
            'cliente': cliente,
            'persona_responsable': persona_responsable
        })
    
    # Obtener listas para filtros
    clientes = Cliente.get_by_tipo('cliente')
    proveedores = Cliente.get_by_tipo('proveedor')
    todos_clientes = clientes + proveedores
    
    estados = ['borrador', 'activo', 'suspendido', 'terminado', 'cancelado']
    
    return render_template('contratos/listar.html', 
                         contratos_data=contratos_data,
                         clientes=todos_clientes,
                         estados=estados,
                         filtros={
                             'cliente_id': cliente_id,
                             'estado': estado,
                             'search': search
                         })

@contratos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crear un nuevo contrato"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            numero_contrato = request.form.get('numero_contrato')
            cliente_id = request.form.get('cliente_id', type=int)
            persona_responsable_id = request.form.get('persona_responsable_id', type=int)
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            monto_original = request.form.get('monto_original', type=float)
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            tipo_contrato = request.form.get('tipo_contrato')
            estado = request.form.get('estado', 'borrador')
            
            # Validaciones básicas
            if not all([numero_contrato, cliente_id, titulo, monto_original, fecha_inicio, fecha_fin]):
                flash('Todos los campos obligatorios deben ser completados', 'error')
                return redirect(url_for('contratos.crear'))
            
            # Crear el contrato
            contrato = Contrato(
                numero_contrato=numero_contrato,
                cliente_id=cliente_id,
                usuario_responsable_id=1,  # TODO: Obtener del usuario actual
                persona_responsable_id=persona_responsable_id if persona_responsable_id else None,
                titulo=titulo,
                descripcion=descripcion,
                monto_original=monto_original,
                monto_actual=monto_original,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado,
                tipo_contrato=tipo_contrato
            )
            
            contrato.save()
            
            # Manejar archivo subido si existe
            if 'archivo_contrato' in request.files:
                archivo = request.files['archivo_contrato']
                if archivo and archivo.filename and allowed_file(archivo.filename):
                    # Crear directorio si no existe
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Generar nombre seguro para el archivo
                    filename = secure_filename(archivo.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    # Guardar archivo
                    archivo.save(filepath)
                    
                    # Crear registro en base de datos
                    documento = DocumentoContrato(
                        contrato_id=contrato.id,
                        nombre_archivo=archivo.filename,
                        ruta_archivo=filepath,
                        tipo_documento='contrato_original',
                        tamaño_archivo=os.path.getsize(filepath),
                        usuario_subida_id=1  # TODO: Obtener del usuario actual
                    )
                    documento.save()
            
            flash('Contrato creado exitosamente', 'success')
            return redirect(url_for('contratos.detalle', id=contrato.id))
            
        except Exception as e:
            flash(f'Error al crear el contrato: {str(e)}', 'error')
            return redirect(url_for('contratos.crear'))
    
    # GET - Mostrar formulario
    clientes = Cliente.get_by_tipo('cliente')
    proveedores = Cliente.get_by_tipo('proveedor')
    todos_clientes = clientes + proveedores
    
    tipos_contrato = ['Servicios', 'Suministros', 'Obra', 'Consultoría', 'Mantenimiento']
    estados = ['borrador', 'activo']
    
    return render_template('contratos/crear.html',
                         clientes=todos_clientes,
                         tipos_contrato=tipos_contrato,
                         estados=estados)

@contratos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalles de un contrato"""
    contrato = Contrato.get_by_id(id)
    if not contrato:
        flash('Contrato no encontrado', 'error')
        return redirect(url_for('contratos.listar'))
    
    cliente = contrato.get_cliente()
    persona_responsable = contrato.get_persona_responsable()
    documentos = contrato.get_documentos()
    suplementos = contrato.get_suplementos()
    
    return render_template('contratos/detalle.html',
                         contrato=contrato,
                         cliente=cliente,
                         persona_responsable=persona_responsable,
                         documentos=documentos,
                         suplementos=suplementos)

@contratos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar un contrato existente"""
    contrato = Contrato.get_by_id(id)
    if not contrato:
        flash('Contrato no encontrado', 'error')
        return redirect(url_for('contratos.listar'))
    
    if request.method == 'POST':
        try:
            # Actualizar datos del contrato
            contrato.numero_contrato = request.form.get('numero_contrato')
            contrato.cliente_id = request.form.get('cliente_id', type=int)
            contrato.persona_responsable_id = request.form.get('persona_responsable_id', type=int) or None
            contrato.titulo = request.form.get('titulo')
            contrato.descripcion = request.form.get('descripcion')
            contrato.monto_original = request.form.get('monto_original', type=float)
            contrato.monto_actual = request.form.get('monto_actual', type=float)
            contrato.fecha_inicio = request.form.get('fecha_inicio')
            contrato.fecha_fin = request.form.get('fecha_fin')
            contrato.estado = request.form.get('estado')
            contrato.tipo_contrato = request.form.get('tipo_contrato')
            
            contrato.save()
            
            flash('Contrato actualizado exitosamente', 'success')
            return redirect(url_for('contratos.detalle', id=contrato.id))
            
        except Exception as e:
            flash(f'Error al actualizar el contrato: {str(e)}', 'error')
    
    # Obtener datos para el formulario
    clientes = Cliente.get_by_tipo('cliente')
    proveedores = Cliente.get_by_tipo('proveedor')
    todos_clientes = clientes + proveedores
    
    personas_responsables = []
    if contrato.cliente_id:
        personas_responsables = PersonaResponsable.get_by_cliente(contrato.cliente_id)
    
    tipos_contrato = ['Servicios', 'Suministros', 'Obra', 'Consultoría', 'Mantenimiento']
    estados = ['borrador', 'activo', 'suspendido', 'terminado', 'cancelado']
    
    return render_template('contratos/editar.html',
                         contrato=contrato,
                         clientes=todos_clientes,
                         personas_responsables=personas_responsables,
                         tipos_contrato=tipos_contrato,
                         estados=estados)

@contratos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar un contrato"""
    contrato = Contrato.get_by_id(id)
    if not contrato:
        return jsonify({'success': False, 'message': 'Contrato no encontrado'})
    
    try:
        # Eliminar documentos asociados
        documentos = contrato.get_documentos()
        for documento in documentos:
            # Eliminar archivo físico
            if os.path.exists(documento.ruta_archivo):
                os.remove(documento.ruta_archivo)
            # Eliminar registro de base de datos
            documento.delete()
        
        # Eliminar contrato
        contrato.delete()
        
        return jsonify({'success': True, 'message': 'Contrato eliminado exitosamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al eliminar el contrato: {str(e)}'})

@contratos_bp.route('/api/personas-por-cliente/<int:cliente_id>')
@login_required
def api_personas_por_cliente(cliente_id):
    """API para obtener personas responsables por cliente"""
    personas = PersonaResponsable.get_by_cliente(cliente_id, activos_solo=True)
    return jsonify([
        {
            'id': persona.id,
            'nombre': persona.nombre,
            'cargo': persona.cargo,
            'es_principal': persona.es_principal
        }
        for persona in personas
    ])

@contratos_bp.route('/<int:id>/subir_documento', methods=['POST'])
@login_required
def subir_documento(id):
    """Subir documento a un contrato"""
    try:
        contrato = Contrato.get_by_id(id)
        if not contrato:
            flash('Contrato no encontrado', 'error')
            return redirect(url_for('contratos.listar'))
        
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('contratos.detalle', id=id))
        
        archivo = request.files['archivo']
        tipo_documento = request.form.get('tipo_documento')
        
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('contratos.detalle', id=id))
        
        if archivo and allowed_file(archivo.filename):
            # Crear directorio si no existe
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Crear nombre único para el archivo
            filename = secure_filename(archivo.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{timestamp}_{filename}"
            
            # Guardar archivo
            upload_path = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            archivo.save(upload_path)
            
            # Crear registro en base de datos
            documento = DocumentoContrato(
                contrato_id=id,
                nombre_archivo=filename,
                ruta_archivo=upload_path,
                tipo_documento=tipo_documento,
                tamaño_archivo=os.path.getsize(upload_path),
                usuario_subida_id=1  # TODO: Obtener del usuario actual
            )
            documento.save()
            
            flash('Documento subido exitosamente', 'success')
        else:
            flash('Tipo de archivo no permitido', 'error')
        
        return redirect(url_for('contratos.detalle', id=id))
    
    except Exception as e:
        flash(f'Error al subir documento: {str(e)}', 'error')
        return redirect(url_for('contratos.detalle', id=id))

@contratos_bp.route('/documentos/<int:documento_id>/eliminar', methods=['POST'])
@login_required
def eliminar_documento(documento_id):
    """Eliminar documento de contrato"""
    try:
        documento = DocumentoContrato.get_by_id(documento_id)
        if not documento:
            return jsonify({'success': False, 'message': 'Documento no encontrado'}), 404
        
        # Eliminar archivo físico
        if os.path.exists(documento.ruta_archivo):
            os.remove(documento.ruta_archivo)
        
        # Eliminar registro de base de datos
        documento.delete()
        
        return jsonify({'success': True, 'message': 'Documento eliminado exitosamente'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@contratos_bp.route('/documentos/<int:documento_id>/descargar')
@login_required
def descargar_documento(documento_id):
    """Descargar documento de contrato"""
    from flask import send_file
    try:
        documento = DocumentoContrato.get_by_id(documento_id)
        if not documento:
            flash('Documento no encontrado', 'error')
            return redirect(url_for('contratos.listar'))
        
        if not os.path.exists(documento.ruta_archivo):
            flash('Archivo no encontrado en el servidor', 'error')
            return redirect(url_for('contratos.listar'))
        
        return send_file(
            documento.ruta_archivo,
            as_attachment=True,
            download_name=documento.nombre_archivo
        )
    
    except Exception as e:
        flash(f'Error al descargar documento: {str(e)}', 'error')
        return redirect(url_for('contratos.listar'))

@contratos_bp.route('/buscar')
@login_required
def buscar():
    """API para búsqueda de contratos"""
    search_term = request.args.get('q', '').strip()
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')
    
    if not search_term:
        return jsonify([])
    
    contratos = Contrato.search(search_term, cliente_id=cliente_id, estado=estado)
    
    results = []
    for contrato in contratos[:10]:  # Limitar a 10 resultados
        cliente = contrato.get_cliente()
        results.append({
            'id': contrato.id,
            'numero_contrato': contrato.numero_contrato,
            'titulo': contrato.titulo,
            'cliente_nombre': cliente.nombre if cliente else 'N/A',
            'estado': contrato.estado,
            'monto_actual': float(contrato.monto_actual) if contrato.monto_actual else 0
        })
    
    return jsonify(results)