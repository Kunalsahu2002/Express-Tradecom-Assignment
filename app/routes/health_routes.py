"""
Health check route — simple liveness endpoint.

Returns 200 if the application is running. Has no database or
external-service dependency, so it always responds when the app is up.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Liveness probe — returns 200 with status ok."""
    return jsonify({
        'success': True,
        'data': {
            'status': 'ok'
        }
    }), 200
