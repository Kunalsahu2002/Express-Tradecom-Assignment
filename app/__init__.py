"""
Flask application factory.

Creates and configures the Flask app, registers extensions, blueprints,
and centralized error handlers.
"""

import os
import logging

from flask import Flask, jsonify
from dotenv import load_dotenv

from app.config import config_by_name
from app.extensions import db, migrate


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Defaults to FLASK_ENV env var or 'development'.

    Returns:
        Configured Flask application instance.
    """
    # Load .env file for local development
    load_dotenv()

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['development']))

    # Configure logging
    _configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _configure_logging(app):
    """Configure application logging using Python's standard logging module."""
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    app.logger.setLevel(log_level)


def _register_blueprints(app):
    """Register all route blueprints with the application."""
    # Import models so Flask-Migrate/Alembic can detect them for migrations
    from app.models import user  # noqa: F401

    from app.routes.health_routes import health_bp
    app.register_blueprint(health_bp)


def _register_error_handlers(app):
    """Register centralized error handlers."""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
