"""
Pytest fixtures for the Flask test client.

Uses SQLite in-memory for test isolation and speed.
Each test function gets a fresh database via the 'client' fixture.
"""

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """
    Create a Flask application configured for testing.

    Uses SQLite in-memory for speed and isolation.
    Session-scoped: the app is created once per test session.
    """
    app = create_app('testing')
    yield app


@pytest.fixture(scope='function')
def client(app):
    """
    Provide a Flask test client with a fresh database per test function.

    Creates all tables before the test and drops them after,
    ensuring complete isolation between tests.
    """
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def sample_user():
    """Return a valid user payload for reuse across tests."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'role': 'admin',
    }


@pytest.fixture
def create_sample_user(client, sample_user):
    """Create a sample user and return the response data."""
    response = client.post('/users', json=sample_user)
    return response.get_json()['data']
