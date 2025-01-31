from flask import Blueprint, jsonify
from app.db import db
from sqlalchemy.sql import text

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Simple endpoint to check if the API is running."""
    return jsonify({"status": "OK"}), 200

@health_bp.route("/db-check", methods=["GET"])
def db_check():
    """Test database connection."""
    try:
        db.session.execute(text("SELECT 1"))  # Simple query to check DB connection
        return jsonify({"database": "Connected"}), 200
    except Exception as e:
        return jsonify({"database": "Error", "message": str(e)}), 500
