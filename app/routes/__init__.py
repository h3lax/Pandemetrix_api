from flask import Blueprint
from app.routes.health import  health_api
from app.routes.continent_routes import continent_api
from app.routes.pays_routes import pays_api
from app.routes.region_routes import region_api
from flask_restx import Api as Api

def register_routes(app):
    """Registers all blueprints to the Flask app."""
    # Initialize Swagger API
    swagger = Api(app, doc="/api/swagger", title="My API", description="API Documentation")

    # Register Namespaces
    swagger.add_namespace(health_api, path="/api/health")
    swagger.add_namespace(continent_api, path="/api/continent")
    swagger.add_namespace(pays_api, path="/api/pays")
    swagger.add_namespace(region_api, path="/api/region")
