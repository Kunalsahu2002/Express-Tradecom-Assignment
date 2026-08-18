"""Tests for validation error shapes and edge cases."""


class TestValidationErrors:
    """Tests for validation error response shape and content."""

    def test_multiple_missing_fields(self, client):
        """Multiple missing fields return all field errors in one response."""
        response = client.post('/users', json={})
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'name' in data['error']
        assert 'email' in data['error']
        assert 'role' in data['error']

    def test_error_response_shape_validation(self, client):
        """Validation errors have the {success: false, error: {...}} shape."""
        response = client.post('/users', json={'name': 'Test'})
        data = response.get_json()

        assert response.status_code == 400
        assert 'success' in data
        assert 'error' in data
        assert data['success'] is False
        assert isinstance(data['error'], dict)

    def test_error_response_shape_not_found(self, client):
        """Not-found errors have the {success: false, error: string} shape."""
        response = client.get('/users/999')
        data = response.get_json()

        assert response.status_code == 404
        assert 'success' in data
        assert 'error' in data
        assert data['success'] is False
        assert isinstance(data['error'], str)

    def test_error_response_shape_duplicate(self, client):
        """Duplicate errors have the {success: false, error: string} shape."""
        user = {'name': 'Test', 'email': 'dupe@example.com', 'role': 'user'}
        client.post('/users', json=user)
        response = client.post('/users', json=user)
        data = response.get_json()

        assert response.status_code == 409
        assert 'success' in data
        assert 'error' in data
        assert data['success'] is False
        assert isinstance(data['error'], str)

    def test_name_too_long(self, client):
        """Name exceeding 100 characters returns 400."""
        response = client.post('/users', json={
            'name': 'A' * 101,
            'email': 'test@example.com',
            'role': 'user',
        })

        assert response.status_code == 400

    def test_role_too_long(self, client):
        """Role exceeding 50 characters returns 400."""
        response = client.post('/users', json={
            'name': 'Test',
            'email': 'test@example.com',
            'role': 'R' * 51,
        })

        assert response.status_code == 400

    def test_whitespace_only_email(self, client):
        """Whitespace-only email returns 400."""
        response = client.post('/users', json={
            'name': 'Test',
            'email': '   ',
            'role': 'user',
        })

        assert response.status_code == 400

    def test_null_fields(self, client):
        """Null values for required fields return 400."""
        response = client.post('/users', json={
            'name': None,
            'email': None,
            'role': None,
        })
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
