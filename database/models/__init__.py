# Importar todas las clases de modelos desde sus archivos separados
from .usuario import Usuario
from .cliente import Cliente
from .proveedor import Proveedor
from .contrato import Contrato
from .suplemento import Suplemento
from .persona_responsable import PersonaResponsable
from .documento_contrato import DocumentoContrato
from .notificacion import Notificacion
from .actividad_sistema import ActividadSistema

# Exportar todas las clases para facilitar la importación
__all__ = [
    'Usuario',
    'Cliente',
    'Proveedor', 
    'Contrato',
    'Suplemento',
    'PersonaResponsable',
    'DocumentoContrato',
    'Notificacion',
    'ActividadSistema'
]