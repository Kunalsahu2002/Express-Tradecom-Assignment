"""
Standard response helpers.

Every route MUST use these functions to build its response.
This ensures the {success, data} / {success, error} contract
is consistent across the entire API.
"""

from flask import jsonify


def success_response(data, status_code=200):
    """
    Build a successful JSON response.

    Args:
        data: The payload to include under the 'data' key.
        status_code: HTTP status code (default 200).

    Returns:
        A Flask Response tuple (json, status_code).
    """
    return jsonify({
        'success': True,
        'data': data,
    }), status_code


def error_response(error, status_code=400):
    """
    Build an error JSON response.

    Args:
        error: A string message or a dict of field-level errors.
        status_code: HTTP status code (default 400).

    Returns:
        A Flask Response tuple (json, status_code).
    """
    return jsonify({
        'success': False,
        'error': error,
    }), status_code
