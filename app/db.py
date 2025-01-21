from flask import current_app, g
import psycopg2
from psycopg2.extras import RealDictCursor  # For dictionary-like row access


def get_db():
    """
    Establishes a PostgreSQL database connection if it doesn't already exist.
    """
    if 'db' not in g:
        g.db = psycopg2.connect(
            host="localhost",
            database="metabase",
            user="metabase",
            password="metabase_password",
            port=5431,
            cursor_factory=RealDictCursor  # To return rows as dictionaries
        )
    return g.db


def close_db(e=None):
    """
    Closes the database connection if it exists.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()
