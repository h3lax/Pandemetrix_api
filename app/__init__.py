from flask import Flask
from config import Config
from app.db import db
from flask_migrate import Migrate
from flask_cors import CORS
from app.routes import register_routes

# Import models
from app import models

def create_app(config_class=Config):
    """Flask application factory pattern."""
    app = Flask(__name__)

    # Enable CORS for the entire app
    CORS(app, origins=["http://localhost:5173"], methods=["GET", "POST"])

    # Load configuration
    app.config.from_object(config_class) # We using the config.py
    app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024  # 20MB


    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db) # TODO: What is this? Not sure it's needed nor in use

    # Register blueprints (routes)
    register_routes(app)

    # hello route
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app