from flask import session
from database.models import Notificacion
from werkzeug.utils import secure_filename
import os


def get_notificaciones_count():
    """
    Obtiene el número de notificaciones no leídas del usuario actual.
    Función helper centralizada para evitar duplicación de código.
    
    Returns:
        int: Número de notificaciones no leídas, 0 si no hay usuario autenticado
    """
    if 'user_id' not in session:
        return 0
    
    try:
        return Notificacion.get_unread_count(session['user_id'])
    except Exception:
        return 0


def get_current_user_id():
    """
    Obtiene el ID del usuario actual de la sesión.
    
    Returns:
        int|None: ID del usuario actual o None si no está autenticado
    """
    return session.get('user_id')


def get_current_username():
    """
    Obtiene el nombre de usuario actual de la sesión.
    
    Returns:
        str|None: Nombre de usuario actual o None si no está autenticado
    """
    return session.get('username')


def is_current_user_admin():
    """
    Verifica si el usuario actual es administrador.
    
    Returns:
        bool: True si es administrador, False en caso contrario
    """
    return session.get('es_admin', False)


# Configuración para subida de archivos
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}


def allowed_file(filename, allowed_extensions=None):
    """
    Verifica si un archivo tiene una extensión permitida.
    
    Args:
        filename (str): Nombre del archivo
        allowed_extensions (set, optional): Extensiones permitidas. 
                                          Si no se especifica, usa ALLOWED_EXTENSIONS
    
    Returns:
        bool: True si la extensión está permitida, False en caso contrario
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def secure_filename_with_timestamp(filename):
    """
    Genera un nombre de archivo seguro con timestamp para evitar colisiones.
    
    Args:
        filename (str): Nombre original del archivo
    
    Returns:
        str: Nombre de archivo seguro con timestamp
    """
    from datetime import datetime
    
    # Obtener nombre seguro
    safe_filename = secure_filename(filename)
    
    # Separar nombre y extensión
    name, ext = os.path.splitext(safe_filename)
    
    # Agregar timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{name}_{timestamp}{ext}"


def format_file_size(size_bytes):
    """
    Formatea el tamaño de archivo en bytes a una representación legible.
    
    Args:
        size_bytes (int): Tamaño en bytes
    
    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def create_success_response(message, data=None):
    """
    Crea una respuesta JSON de éxito estandarizada.
    
    Args:
        message (str): Mensaje de éxito
        data (dict, optional): Datos adicionales
    
    Returns:
        dict: Respuesta JSON estandarizada
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data:
        response.update(data)
    
    return response


def create_error_response(message, error_code=None, data=None):
    """
    Crea una respuesta JSON de error estandarizada.
    
    Args:
        message (str): Mensaje de error
        error_code (str, optional): Código de error
        data (dict, optional): Datos adicionales
    
    Returns:
        dict: Respuesta JSON estandarizada
    """
    response = {
        'success': False,
        'message': message
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if data:
        response.update(data)
    
    return response


def validate_required_fields(data, required_fields):
    """
    Valida que los campos requeridos estén presentes en los datos.
    
    Args:
        data (dict): Datos a validar
        required_fields (list): Lista de campos requeridos
    
    Returns:
        tuple: (bool, list) - (es_valido, campos_faltantes)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields