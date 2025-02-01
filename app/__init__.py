from flask import Flask
from config import Config
from app.db import db
from flask_migrate import Migrate
from app.routes import register_routes

# Import models
from app import models


def create_app(config_class=Config):
    """Flask application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class) # We using the config.py

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints (routes)
    register_routes(app)

    # hello route
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    
    """ @app.route('/test-db')
    def test_db():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute('SELECT NOW();')
            result = cursor.fetchone()
        return {'current_time': result['now']} """

    return app