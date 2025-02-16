from flask_restx import Namespace, Resource, fields
from app.db import db
from sqlalchemy.sql import text

# Define Namespace (NO Blueprint anymore)
health_api = Namespace("health", description="Health check related operations")

# Define response models
health_model = health_api.model("Health", {
    "status": fields.String(required=True, description="Status of the API")
})

db_check_model = health_api.model("DBCheck", {
    "database": fields.String(required=True, description="Database connection status"),
    "message": fields.String(description="Error message")
})

@health_api.route("/status")
class HealthCheck(Resource):
    @health_api.marshal_with(health_model)
    def get(self):
        """Simple endpoint to check if the API is running."""
        return {"status": "OK"}, 200

@health_api.route("/db-check")
class DBCheck(Resource):
    @health_api.marshal_with(db_check_model)
    def get(self):
        """Test database connection."""
        try:
            db.session.execute(text("SELECT 1"))  # Simple query to check DB connection
            return {"database": "Connected"}, 200
        except Exception as e:
            return {"database": "Error", "message": str(e)}, 500
