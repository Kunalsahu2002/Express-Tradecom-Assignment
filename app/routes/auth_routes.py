"""
Authentication routes — JWT login endpoint.

Provides a simple credential-based login that issues JWT access tokens.
Uses a demo credential pair from environment variables — this is NOT
a production-grade auth system, just a bonus feature demonstration.
"""

import os

from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)

# Demo credentials from environment variables
# In a real system, these would come from a user/credentials table
DEMO_USERNAME = os.environ.get('DEMO_USERNAME', 'admin')
DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD', 'password123')


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authenticate and receive a JWT access token.

    Expects JSON body with 'username' and 'password'.
    Returns 200 with access_token on success, 401 on invalid credentials.
    """
    json_data = request.get_json(silent=True)

    if json_data is None:
        return error_response('Request body must be JSON', 400)

    username = json_data.get('username', '')
    password = json_data.get('password', '')

    if username == DEMO_USERNAME and password == DEMO_PASSWORD:
        access_token = create_access_token(identity=username)
        return success_response({'access_token': access_token}, 200)

    return error_response('Invalid credentials', 401)
