"""
Extension instances — single init point, avoids circular imports.

db and migrate are instantiated here without an app. They are bound
to the Flask app via init_app() inside the app factory (app/__init__.py).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
