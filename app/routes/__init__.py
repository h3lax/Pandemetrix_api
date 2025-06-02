from app.routes.health import  health_api
from app.routes.continent_routes import continent_api
from app.routes.pays_routes import pays_api
from app.routes.region_routes import region_api
from app.routes.rapport_routes import rapport_api
from app.routes.periode_routes import periode_api
from app.routes.maladie_routes import maladie_api
from app.routes.concerne_routes import concerne_api
from app.routes.filtered_data import filtered_data_ns
from app.routes.etl_service import etl_ns
from flask_restx import Api as Api

def register_routes(app):
    """Registers all blueprints to the Flask app."""
    # Initialize Swagger API
    swagger = Api(app, doc="/api/swagger", title="Pandemetrix", description="API Documentation")

    # Register Namespaces
    swagger.add_namespace(health_api, path="/api/health")
    swagger.add_namespace(continent_api, path="/api/continent")
    swagger.add_namespace(pays_api, path="/api/pays")
    swagger.add_namespace(region_api, path="/api/region")
    swagger.add_namespace(rapport_api, path="/api/rapport")
    swagger.add_namespace(periode_api, path="/api/periode")
    swagger.add_namespace(maladie_api, path="/api/maladie")
    swagger.add_namespace(concerne_api, path="/api/concerne")
    swagger.add_namespace(filtered_data_ns, path="/api/data")
    swagger.add_namespace(etl_ns, path="/api/etl")
    