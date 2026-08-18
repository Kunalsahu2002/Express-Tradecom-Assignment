"""Tests for GET /users and GET /users/<id> — user retrieval endpoints."""


class TestGetUsers:
    """Tests for listing and retrieving users."""

    def test_get_all_users(self, client):
        """GET /users returns all seeded users with correct total."""
        # Seed some users
        users_to_create = [
            {'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'},
            {'name': 'Bob', 'email': 'bob@example.com', 'role': 'user'},
            {'name': 'Charlie', 'email': 'charlie@example.com', 'role': 'editor'},
        ]
        for user in users_to_create:
            client.post('/users', json=user)

        response = client.get('/users')
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['total'] == 3
        assert len(data['data']['users']) == 3

    def test_get_all_users_empty(self, client):
        """GET /users with no users returns empty array, not 404."""
        response = client.get('/users')
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['users'] == []
        assert data['data']['total'] == 0

    def test_get_user_by_id(self, client, sample_user):
        """GET /users/<id> returns the correct user object."""
        # Create a user first
        create_resp = client.post('/users', json=sample_user)
        user_id = create_resp.get_json()['data']['id']

        response = client.get(f'/users/{user_id}')
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['id'] == user_id
        assert data['data']['name'] == sample_user['name']
        assert data['data']['email'] == sample_user['email']
        assert data['data']['role'] == sample_user['role']

    def test_get_user_not_found(self, client):
        """GET /users/<id> for nonexistent user returns 404."""
        response = client.get('/users/999')
        data = response.get_json()

        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()

    def test_get_users_returns_pagination_metadata(self, client, sample_user):
        """GET /users response includes correct pagination metadata."""
        client.post('/users', json=sample_user)

        response = client.get('/users')
        data = response.get_json()

        assert response.status_code == 200
        assert 'total' in data['data']
        assert 'page' in data['data']
        assert 'limit' in data['data']
        assert 'pages' in data['data']
        assert data['data']['page'] == 1
        assert data['data']['limit'] == 10
