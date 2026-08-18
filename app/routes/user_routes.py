"""
User routes — all /users endpoints.

This is a thin controller layer: parse request, validate input,
call one service method, wrap the result via response helpers.
No business logic, no direct DB access, no raw SQLAlchemy queries.
"""

from flask import Blueprint, request

from app.schemas.user_schema import UserSchema
from app.services.user_service import UserService
from app.utils.responses import success_response, error_response

users_bp = Blueprint('users', __name__)
user_schema = UserSchema()


@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.

    Expects JSON body with 'name', 'email', 'role'.
    Returns 201 on success, 400 on validation error, 409 on duplicate email.
    """
    json_data = request.get_json()

    if not json_data:
        return error_response('Request body must be JSON', 400)

    # Validate input via Marshmallow schema
    errors = user_schema.validate(json_data)
    if errors:
        return error_response(errors, 400)

    # Load (deserialize + validate) the data
    validated_data = user_schema.load(json_data)

    # Delegate to service layer
    result = UserService.create_user(validated_data)
    return success_response(result, 201)


@users_bp.route('/users', methods=['GET'])
def get_users():
    """
    List all users with optional search and pagination.

    Query params:
        search (str, optional): Filter by name or email (case-insensitive substring).
        page (int, optional): Page number, default 1.
        limit (int, optional): Results per page, default 10, max 100.
    """
    # Parse search parameter
    search = request.args.get('search', None)

    # Parse and validate pagination parameters
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')

    try:
        page = int(page)
        limit = int(limit)
    except (ValueError, TypeError):
        return error_response('Invalid pagination parameters', 400)

    if page < 1 or limit < 1:
        return error_response('Invalid pagination parameters', 400)

    # Delegate to service layer
    result = UserService.get_users(search=search, page=page, limit=limit)
    return success_response(result, 200)


@users_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Retrieve a single user by ID.

    Returns 200 on success, 404 if not found.
    """
    result = UserService.get_user_by_id(id)
    return success_response(result, 200)
