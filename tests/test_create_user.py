"""Tests for POST /users — user creation endpoint."""


class TestCreateUser:
    """Tests for creating users via POST /users."""

    def test_create_user_success(self, client, sample_user, auth_headers):
        """Valid user creation returns 201 with user data."""
        response = client.post('/users', json=sample_user, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['name'] == sample_user['name']
        assert data['data']['email'] == sample_user['email']
        assert data['data']['role'] == sample_user['role']
        assert 'id' in data['data']

    def test_create_user_missing_name(self, client, auth_headers):
        """Missing 'name' field returns 400 with field-level error."""
        response = client.post('/users', json={
            'email': 'test@example.com',
            'role': 'user',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'name' in data['error']

    def test_create_user_missing_email(self, client, auth_headers):
        """Missing 'email' field returns 400 with field-level error."""
        response = client.post('/users', json={
            'name': 'Test User',
            'role': 'user',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'email' in data['error']

    def test_create_user_missing_role(self, client, auth_headers):
        """Missing 'role' field returns 400 with field-level error."""
        response = client.post('/users', json={
            'name': 'Test User',
            'email': 'test@example.com',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'role' in data['error']

    def test_create_user_invalid_email(self, client, auth_headers):
        """Invalid email format returns 400 with email field error."""
        response = client.post('/users', json={
            'name': 'Test User',
            'email': 'not-an-email',
            'role': 'user',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'email' in data['error']

    def test_create_user_duplicate_email(self, client, sample_user, auth_headers):
        """Duplicate email returns 409 with appropriate error message."""
        # Create the first user
        client.post('/users', json=sample_user, headers=auth_headers)

        # Attempt to create another user with the same email
        response = client.post('/users', json={
            'name': 'Another User',
            'email': sample_user['email'],
            'role': 'editor',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 409
        assert data['success'] is False
        assert 'already exists' in data['error'].lower()

    def test_create_user_whitespace_only_name(self, client, auth_headers):
        """Whitespace-only name is treated as missing and returns 400."""
        response = client.post('/users', json={
            'name': '   ',
            'email': 'test@example.com',
            'role': 'user',
        }, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_create_user_no_json_body(self, client, auth_headers):
        """Request without JSON body returns 400."""
        response = client.post('/users', content_type='application/json',
                               data='not valid json', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_create_user_empty_json_body(self, client, auth_headers):
        """Empty JSON body returns 400 with field-level errors."""
        response = client.post('/users', json={}, headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'name' in data['error']
        assert 'email' in data['error']
        assert 'role' in data['error']

    def test_create_user_without_token(self, client, sample_user):
        """POST /users without JWT token returns 401."""
        response = client.post('/users', json=sample_user)
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False

    def test_create_user_with_invalid_token(self, client, sample_user):
        """POST /users with invalid JWT token returns 401."""
        response = client.post('/users', json=sample_user,
                               headers={'Authorization': 'Bearer invalid-token'})
        data = response.get_json()

        assert response.status_code == 401
        assert data['success'] is False
