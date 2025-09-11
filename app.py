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

# Registrar blueprints
register_blueprints(app)

# Registrar blueprint de API para inicialización de datos
from routes.init_data_api import init_data_api
app.register_blueprint(init_data_api)

def init_db():
    """Inicializa la base de datos y crea el usuario administrador"""
    # Inicializar la base de datos explícitamente
    db_manager.init_database()
    
    # Crear usuario administrador automáticamente
    from services.init_data_service import InitDataService
    init_service = InitDataService()
    init_service.crear_usuario_admin_obligatorio()
    
    print("Base de datos inicializada correctamente.")

# Inicializar la base de datos al arrancar la aplicación
with app.app_context():
    init_db()

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