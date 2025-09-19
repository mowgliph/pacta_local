from flask import Blueprint
from .auth import auth_bp
from .main import main_bp
from .users import users_bp
from .notifications import notifications_bp
from .personas import personas_bp, api_personas_bp
from .contratos import contratos_bp
from .changelog import changelog_bp
from .backup_routes import backup_bp
from .document_routes import document_bp
from .providers import providers_bp
from .clients import clients_bp
from .suplementos import suplementos_bp

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(providers_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(api_personas_bp)
    app.register_blueprint(contratos_bp)
    app.register_blueprint(changelog_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(suplementos_bp)