from flask import Blueprint
from app.routes.health import health_bp
from app.routes.continent_routes import continent_bp

def register_routes(app):
    """Registers all blueprints to the Flask app."""
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(continent_bp, url_prefix="/api")
