"""Tests for search and pagination functionality on GET /users."""


def _seed_users(client, count=15):
    """Helper to seed multiple users for pagination/search tests."""
    users = []
    for i in range(1, count + 1):
        user = {
            'name': f'User {i}',
            'email': f'user{i}@example.com',
            'role': 'admin' if i % 3 == 0 else 'user',
        }
        resp = client.post('/users', json=user)
        users.append(resp.get_json()['data'])
    return users


class TestSearch:
    """Tests for the search query parameter."""

    def test_search_by_name(self, client):
        """Search by partial name returns matching users only."""
        client.post('/users', json={'name': 'Alice Johnson', 'email': 'alice@example.com', 'role': 'admin'})
        client.post('/users', json={'name': 'Bob Smith', 'email': 'bob@example.com', 'role': 'user'})

        response = client.get('/users?search=alice')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['total'] == 1
        assert data['data']['users'][0]['name'] == 'Alice Johnson'

    def test_search_by_email(self, client):
        """Search by partial email returns matching users only."""
        client.post('/users', json={'name': 'Alice', 'email': 'alice@domain.com', 'role': 'admin'})
        client.post('/users', json={'name': 'Bob', 'email': 'bob@other.com', 'role': 'user'})

        response = client.get('/users?search=domain')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['total'] == 1
        assert data['data']['users'][0]['email'] == 'alice@domain.com'

    def test_search_no_results(self, client):
        """Search with no matches returns empty array, still 200."""
        client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'})

        response = client.get('/users?search=zzz-nomatch')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['users'] == []
        assert data['data']['total'] == 0

    def test_search_case_insensitive(self, client):
        """Search is case-insensitive."""
        client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'})

        response = client.get('/users?search=ALICE')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['total'] == 1


class TestPagination:
    """Tests for pagination query parameters."""

    def test_default_pagination(self, client):
        """Without pagination params, defaults to page=1, limit=10."""
        _seed_users(client, 15)

        response = client.get('/users')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['page'] == 1
        assert data['data']['limit'] == 10
        assert len(data['data']['users']) == 10
        assert data['data']['total'] == 15
        assert data['data']['pages'] == 2

    def test_custom_page_and_limit(self, client):
        """Custom page and limit return correct offset results."""
        _seed_users(client, 15)

        response = client.get('/users?page=2&limit=5')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['page'] == 2
        assert data['data']['limit'] == 5
        assert len(data['data']['users']) == 5
        assert data['data']['total'] == 15
        assert data['data']['pages'] == 3

    def test_invalid_page_string(self, client):
        """Non-integer page returns 400."""
        response = client.get('/users?page=abc')
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False
        assert 'pagination' in data['error'].lower()

    def test_invalid_limit_negative(self, client):
        """Negative limit returns 400."""
        response = client.get('/users?limit=-5')
        data = response.get_json()

        assert response.status_code == 400
        assert data['success'] is False

    def test_empty_page_beyond_range(self, client):
        """Page beyond available data returns empty array, not 404."""
        _seed_users(client, 5)

        response = client.get('/users?page=999')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['users'] == []
        assert data['data']['total'] == 5

    def test_limit_capped_at_100(self, client):
        """Limit above 100 is clamped to 100."""
        _seed_users(client, 5)

        response = client.get('/users?limit=500')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['limit'] == 100


class TestSearchWithPagination:
    """Tests for combined search and pagination."""

    def test_search_with_pagination(self, client):
        """Search and pagination work together — paginate the filtered set."""
        # Create 10 users with 'test' in the name and 5 without
        for i in range(1, 11):
            client.post('/users', json={
                'name': f'Test User {i}',
                'email': f'test{i}@example.com',
                'role': 'user',
            })
        for i in range(1, 6):
            client.post('/users', json={
                'name': f'Other {i}',
                'email': f'other{i}@example.com',
                'role': 'admin',
            })

        # Search for 'test' with page=2, limit=5
        response = client.get('/users?search=test&page=2&limit=5')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['total'] == 10  # 10 matching users
        assert data['data']['page'] == 2
        assert data['data']['limit'] == 5
        assert len(data['data']['users']) == 5
        assert data['data']['pages'] == 2

    def test_search_with_pagination_partial_last_page(self, client):
        """Last page of search results may have fewer items than limit."""
        for i in range(1, 8):
            client.post('/users', json={
                'name': f'Match {i}',
                'email': f'match{i}@example.com',
                'role': 'user',
            })

        response = client.get('/users?search=match&page=2&limit=5')
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['total'] == 7
        assert len(data['data']['users']) == 2  # Only 2 left on page 2
        assert data['data']['pages'] == 2
