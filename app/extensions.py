"""
Extension instances — single init point, avoids circular imports.

db, migrate, and jwt are instantiated here without an app. They are bound
to the Flask app via init_app() inside the app factory (app/__init__.py).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
