from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, session
from werkzeug.utils import secure_filename
from database.models import Contrato, Cliente, PersonaResponsable, DocumentoContrato, Suplemento, Usuario, Proveedor, Notificacion
from .decorators import login_required
from .utils import get_notificaciones_count, allowed_file, get_current_user_id, create_success_response, create_error_response
from datetime import datetime
import os

contratos_bp = Blueprint('contratos', __name__, url_prefix='/contratos')

# Configuración para subida de archivos
UPLOAD_FOLDER = 'uploads/contratos'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

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
    
    # Datos adicionales para el modal de crear contrato
    tipos_contrato = ['Servicios', 'Suministros', 'Obra', 'Consultoría', 'Mantenimiento']
    estados_modal = ['borrador', 'activo']
    
    # Obtener usuario actual de la sesión
    usuario_actual = Usuario.get_by_id(session['user_id'])
    
    # Calcular estadísticas para el template
    total_contratos = len(contratos_data)
    contratos_activos = len([c for c in contratos_data if c['contrato'].estado == 'activo'])
    
    # Calcular valor total de contratos activos
    valor_total = sum([c['contrato'].monto_actual for c in contratos_data if c['contrato'].estado == 'activo'])
    valor_total_formatted = f"{valor_total/1000000:.1f}M" if valor_total > 1000000 else f"{valor_total:,.0f}"
    
    # Contratos próximos a vencer (30 días)
    from datetime import datetime, timedelta
    fecha_limite = datetime.now().date() + timedelta(days=30)
    proximos_vencer = 0
    
    for contrato_data in contratos_data:
        contrato = contrato_data['contrato']
        if contrato.estado == 'activo' and contrato.fecha_fin:
            try:
                if isinstance(contrato.fecha_fin, str):
                    fecha_fin = datetime.strptime(contrato.fecha_fin, '%Y-%m-%d').date()
                else:
                    fecha_fin = contrato.fecha_fin
                
                if fecha_fin <= fecha_limite:
                    proximos_vencer += 1
            except (ValueError, TypeError):
                continue
    
    # Calcular contratos pendientes y vencidos
    contratos_pendientes = len([c for c in contratos_data if c['contrato'].estado == 'borrador'])
    contratos_vencidos = 0
    
    # Calcular contratos vencidos (fecha_fin pasada)
    from datetime import datetime
    fecha_actual = datetime.now().date()
    
    for contrato_data in contratos_data:
        contrato = contrato_data['contrato']
        if contrato.estado == 'activo' and contrato.fecha_fin:
            try:
                if isinstance(contrato.fecha_fin, str):
                    fecha_fin = datetime.strptime(contrato.fecha_fin, '%Y-%m-%d').date()
                else:
                    fecha_fin = contrato.fecha_fin
                
                if fecha_fin < fecha_actual:
                    contratos_vencidos += 1
            except (ValueError, TypeError):
                continue
    
    contratos_stats = {
        'total': total_contratos,
        'activos': contratos_activos,
        'pendientes': contratos_pendientes,
        'vencidos': contratos_vencidos
    }
    
    estadisticas = {
        'total_contratos': total_contratos,
        'contratos_activos': contratos_activos,
        'proximos_vencer': proximos_vencer,
        'valor_total': valor_total_formatted
    }
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('contratos.html', 
                         contratos_data=contratos_data,
                         clientes=todos_clientes,
                         estados=estados,
                         tipos_contrato=tipos_contrato,
                         estados_modal=estados_modal,
                         usuario=usuario_actual,
                         estadisticas=estadisticas,
                         contratos_stats=contratos_stats,
                         notificaciones_count=notificaciones_count,
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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('contratos/crear.html',
                         clientes=todos_clientes,
                         tipos_contrato=tipos_contrato,
                         estados=estados,
                         notificaciones_count=notificaciones_count)

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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('contratos/detalle.html',
                         contrato=contrato,
                         cliente=cliente,
                         persona_responsable=persona_responsable,
                         documentos=documentos,
                         suplementos=suplementos,
                         notificaciones_count=notificaciones_count)

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
    
    # Obtener contador de notificaciones
    notificaciones_count = get_notificaciones_count()
    
    return render_template('contratos/editar.html',
                         contrato=contrato,
                         clientes=todos_clientes,
                         personas_responsables=personas_responsables,
                         tipos_contrato=tipos_contrato,
                         estados=estados,
                         notificaciones_count=notificaciones_count)

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

# Ruta movida a api_personas_bp en personas.py para mantener consistencia

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

@contratos_bp.route('/vencidos')
@login_required
def contratos_vencidos():
    """Página de contratos vencidos"""
    try:
        from datetime import date
        
        # Obtener contratos vencidos
        contratos_vencidos = Contrato.get_expired_contracts()
        
        # Calcular días vencidos para cada contrato
        for contrato in contratos_vencidos:
            if contrato.fecha_fin:
                dias_vencido = (date.today() - contrato.fecha_fin).days
                contrato.dias_vencido = dias_vencido
            else:
                contrato.dias_vencido = 0
        
        # Obtener listas para filtros
        try:
            proveedores = Proveedor.get_all()
        except:
            proveedores = []  # Si no existe la tabla proveedores
        clientes = Cliente.get_all()
        
        # Obtener usuario actual
        usuario = Usuario.get_by_id(session.get('user_id'))
        
        # Obtener contador de notificaciones
        notificaciones_count = get_notificaciones_count()
        
        return render_template('contratos-vencidos.html', 
                             contratos_vencidos=contratos_vencidos,
                             proveedores=proveedores,
                             clientes=clientes,
                             usuario=usuario,
                             notificaciones_count=notificaciones_count)
    
    except Exception as e:
        flash(f'Error al cargar contratos vencidos: {str(e)}', 'error')
        return redirect(url_for('contratos.listar'))