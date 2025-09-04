from flask import Blueprint
from .auth import auth_bp
from .main import main_bp
from .users import users_bp
from .notifications import notifications_bp
from .personas import personas_bp
from .contratos import contratos_bp

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(contratos_bp)