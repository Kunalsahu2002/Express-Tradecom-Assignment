# User Management REST API

A Flask-based REST API for user management, backed by MySQL. Built as a backend evaluation project demonstrating clean modular architecture, proper validation, error handling, and testing.

## Features

- **CRUD Operations**: Create, list, and retrieve users
- **Search**: Filter users by name or email (case-insensitive substring matching)
- **Pagination**: Configurable page size with metadata (total, pages, current page)
- **Input Validation**: Required field checks, email format validation via Marshmallow
- **Error Handling**: Centralized exception handling with consistent JSON error responses
- **JWT Authentication** (Bonus): Token-based auth for write operations
- **Docker Support** (Bonus): Containerized deployment with docker-compose

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Flask 3.x |
| Database | MySQL 8.x |
| ORM | Flask-SQLAlchemy (SQLAlchemy 2.x) |
| Migrations | Flask-Migrate (Alembic) |
| Validation | Marshmallow |
| Authentication | Flask-JWT-Extended |
| Testing | pytest + Flask test client |
| Containerization | Docker + docker-compose |
| WSGI Server | Gunicorn (Docker) |
| DB Driver | PyMySQL |

## Architecture

```
Client
  ↓
Route (Flask Blueprint) — parses request, delegates to schema for validation
  ↓
Schema (Marshmallow) — validates & deserializes input
  ↓
Service Layer — business logic: duplicate checks, search, pagination
  ↓
Model (SQLAlchemy) — persistence mapping
  ↓
MySQL
  ↓
Service — returns plain dict, never raw ORM objects
  ↓
Route — wraps result in standard {success, data} envelope
  ↓
JSON Response
```

**Layer responsibilities**:
- **Routes**: HTTP-only concerns. No business logic, no direct DB access.
- **Schemas**: Field-level validation rules. Never touches the database.
- **Services**: All business logic. The only layer that queries models/db.
- **Models**: SQLAlchemy table definitions only. No business logic.

## Project Structure

```
user-management-api/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Extension instances (db, migrate, jwt)
│   ├── exceptions.py        # Custom exception classes
│   ├── models/
│   │   └── user.py          # User SQLAlchemy model
│   ├── schemas/
│   │   └── user_schema.py   # Marshmallow validation schema
│   ├── routes/
│   │   ├── health_routes.py # GET /health
│   │   ├── user_routes.py   # /users endpoints
│   │   └── auth_routes.py   # POST /auth/login (JWT)
│   ├── services/
│   │   └── user_service.py  # User business logic
│   └── utils/
│       └── responses.py     # Standard response helpers
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_create_user.py
│   ├── test_get_users.py
│   ├── test_search_pagination.py
│   └── test_validation_errors.py
├── migrations/              # Flask-Migrate generated
├── postman/
│   └── user_api.postman_collection.json
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py                   # Entry point
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Python 3.11+
- MySQL 8.x (running locally or via Docker)
- pip
- Docker & docker-compose (optional, for containerized deployment)

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Kunalsahu2002/Express-Tradecom-Assignment.git
cd Express-Tradecom-Assignment
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your actual MySQL credentials
```

### 5. Create the MySQL database
```sql
CREATE DATABASE IF NOT EXISTS users;
```

### 6. Run database migrations
```bash
flask db upgrade
```

### 7. Start the application
```bash
python run.py
```

The API will be available at `http://localhost:5000`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Flask secret key | (required) |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | (required) |
| `DB_NAME` | MySQL database name | `users` |
| `JWT_SECRET_KEY` | JWT signing key | (required) |
| `DEMO_USERNAME` | Demo login username | `admin` |
| `DEMO_PASSWORD` | Demo login password | `password123` |

See `.env.example` for placeholder values.

## MySQL Setup

### Option 1: Manual setup
```sql
CREATE DATABASE IF NOT EXISTS users;
USE users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Option 2: Using Flask-Migrate
```bash
flask db upgrade
```

## Database Schema

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

| Column | Type | Constraints |
|---|---|---|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `name` | VARCHAR(100) | NOT NULL |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE |
| `role` | VARCHAR(50) | NOT NULL |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

## Running the Application

### Local Development
```bash
python run.py
```

### Docker
```bash
# Start both MySQL and the Flask app
docker-compose up --build

# The API will be available at http://localhost:5000
# MySQL runs on port 3307 (externally) to avoid conflict with local MySQL
```

**Note**: When using Docker, `DB_HOST` is automatically set to `db` (the Docker service name). For local development, use `localhost`.

## API Documentation

### Authentication

#### `POST /auth/login`
Authenticate and receive a JWT access token.

**Request:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**Response (401):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

### Users

#### `POST /users` 🔒 (Requires JWT)
Create a new user.

**Request:**
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"name": "John Doe", "email": "john@example.com", "role": "admin"}'
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
  }
}
```

#### `GET /users`
List all users with optional search and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | string | - | Filter by name or email (case-insensitive) |
| `page` | int | 1 | Page number |
| `limit` | int | 10 | Results per page (max 100) |

**Request:**
```bash
# List all users
curl http://localhost:5000/users

# Search by name
curl "http://localhost:5000/users?search=john"

# Paginate
curl "http://localhost:5000/users?page=2&limit=5"

# Combined
curl "http://localhost:5000/users?search=john&page=1&limit=10"
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 10,
    "pages": 1
  }
}
```

#### `GET /users/<id>`
Retrieve a single user by ID.

**Request:**
```bash
curl http://localhost:5000/users/1
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
  }
}
```

#### `GET /health`
Liveness check — no database dependency.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "ok"
  }
}
```

## Error Responses

| Status | Scenario | Error Format |
|---|---|---|
| 400 | Validation error | `{"success": false, "error": {"field": ["message"]}}` |
| 400 | Invalid pagination | `{"success": false, "error": "Invalid pagination parameters"}` |
| 401 | Missing/invalid JWT | `{"success": false, "error": "Missing or invalid authorization token"}` |
| 404 | User not found | `{"success": false, "error": "User not found"}` |
| 409 | Duplicate email | `{"success": false, "error": "A user with this email already exists."}` |
| 500 | Server error | `{"success": false, "error": "Internal server error"}` |

## Testing

Tests use SQLite in-memory for speed and isolation.

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_create_user.py -v

# Run with coverage (if coverage is installed)
pytest --cov=app -v
```

**Test coverage:**
- `test_create_user.py` — 11 tests (valid creation, missing fields, invalid email, duplicate, whitespace, JWT auth)
- `test_get_users.py` — 7 tests (list, get by ID, not found, pagination metadata, public access)
- `test_search_pagination.py` — 12 tests (search by name/email, no results, case-insensitive, pagination, combined)
- `test_validation_errors.py` — 8 tests (multiple missing fields, error shapes, length limits, null values)

**Test DB trade-off**: Tests use SQLite in-memory instead of a separate MySQL test database. This provides faster test execution and zero external dependencies, but SQLite doesn't enforce all MySQL constraint behaviors identically (e.g., string length enforcement). The production MySQL database has the authoritative constraint definitions.

## Git Workflow

```
main
  ↓
assignment (all feature work)
  ↓
PR: assignment → main
```

Commits follow Conventional Commits style (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).

## Assumptions

1. **`created_at` column**: Added beyond the assignment's literal spec (which only specifies `id`, `name`, `email`, `role`) for practical timestamping. Not included in JSON responses to keep the API contract aligned with the spec's examples.

2. **`name` length limit (100 chars)**: Not specified in the assignment; chosen as a reasonable bound documented here.

3. **`role` length limit (50 chars)**: Same as above — reasonable bound, not from the spec.

4. **`limit` cap at 100**: Pagination `limit` values above 100 are clamped to 100 to prevent excessive query sizes. This is a design decision, not a spec requirement.

5. **Non-integer URL path IDs**: Flask's `<int:id>` converter automatically returns 404 for non-integer path segments. This is accepted default behavior.

6. **Email case sensitivity**: Relies on MySQL's default collation (case-insensitive), which is correct behavior for email addresses.

7. **JWT scope**: Only `POST /users` (write operation) is protected. Read endpoints (`GET /users`, `GET /users/<id>`) remain public to keep the core grading surface unaffected by auth.

8. **Demo credentials**: JWT uses a simple env-var-based demo credential pair (`admin`/`password123`), not a full user-account system. This is intentional — the assignment scope does not require a complete authentication backend.

9. **Test database**: Tests use SQLite in-memory for speed/isolation. This is a documented trade-off — SQLite doesn't enforce all MySQL behaviors identically.

## Short Answers (Task 7)

### 1. Why did you choose Flask?

Flask was chosen because the assignment explicitly requires a hand-designed modular structure with separate `/routes`, `/models`, and `/services` folders. Flask gives full visibility into every architectural decision — there's no framework-generated scaffolding hiding how the layers connect, which matters both for grading and for the ability to explain every part of the code. Additionally, since this is an API-first project with no HTML templates or frontend, Flask's lightweight nature is a perfect fit: it provides exactly the HTTP layer needed without unnecessary overhead from features like Django's admin panel, template engine, or built-in ORM conventions.

### 2. How would you scale this system?

Starting from this project's actual architecture:

- **Horizontal scaling**: Flask is stateless per-request, so multiple instances can run behind a load balancer (e.g., Nginx, AWS ALB) without session-sharing concerns.
- **Database read replicas**: Separate read traffic (GET endpoints, which dominate typical usage) from writes (POST) using MySQL read replicas.
- **Connection pooling**: Use SQLAlchemy's built-in connection pool settings or PgBouncer-equivalent for MySQL to handle concurrent connections efficiently.
- **Caching**: Cache common `GET /users` query results (especially paginated lists) using Redis, with invalidation on POST/update operations.
- **Database indexing**: Add indexes on `name` and `email` columns for the `search` query if the dataset grows large — `ilike` on un-indexed columns becomes expensive at scale.
- **API rate limiting**: Add per-client rate limits (e.g., Flask-Limiter) to prevent abuse.

### 3. What changes would you make for production?

Based on this project's actual gaps:

- **WSGI server**: Already using Gunicorn in the Docker image; for non-Docker deployments, swap Flask's dev server for Gunicorn/uWSGI behind a reverse proxy (Nginx).
- **Secrets management**: Replace `.env` files with a proper secrets manager (AWS Secrets Manager, HashiCorp Vault) — `.env` files are a deployment risk.
- **HTTPS**: Terminate TLS at the reverse proxy or load balancer level.
- **Centralized logging & monitoring**: Integrate structured logging (JSON format) with a log aggregation service (ELK, CloudWatch). Add application monitoring (Prometheus, Datadog).
- **CI/CD pipeline**: Automated testing, linting, and deployment on every push.
- **Rate limiting**: Protect endpoints from abuse, especially `POST /users`.
- **Full authentication**: Expand beyond demo credentials to a proper user-credential system with password hashing (bcrypt), refresh tokens, and role-based access control.
- **Database migrations in CI**: Run migrations as part of the deployment pipeline, not manually.
- **Health check enhancements**: Add a `/ready` endpoint that verifies DB connectivity, separate from the lightweight `/health` liveness check.

## AI Usage Declaration

**Tools used**: Antigravity AI (Claude)

**AI-assisted**:
- Project structure scaffolding and boilerplate code generation
- Implementation of application services
- Test suite generation
- README and documentation drafting

**Manually written/modified**:
- Implementation plan and architectural decisions
- Specification review and requirement mapping
- Implementation of Routes, models, and schemas
- Environment configuration with actual credentials
- Docker configuration
- JWT authentication integration
- All code was reviewed and understood before committing

**Verification**:
- Full pytest suite (38 tests) executed and passing
- Manual API verification against all 14 scenarios in the verification checklist
- Database schema verified against specification
- All error response shapes verified against the JSON contract

## Bonus Features

### ✅ Docker
- `Dockerfile` using Python 3.11-slim with Gunicorn
- `docker-compose.yml` with Flask app + MySQL 8 services
- MySQL health check ensures app starts only after DB is ready
- `docker-compose up --build` produces a fully working API

### ✅ JWT Authentication
- `POST /auth/login` — issues JWT access tokens
- `POST /users` protected with `@jwt_required()`
- `GET /users` and `GET /users/<id>` remain public (no auth required)
- Demo credentials: `admin` / `password123` (configurable via env vars)
- Consistent 401 error responses for missing/invalid/expired tokens

## Future Improvements

> **Note**: These are ideas only — none are implemented in this submission.

- **Rate limiting**: Per-client request throttling (Flask-Limiter)
- **Role-based access control (RBAC)**: Fine-grained permissions beyond simple JWT auth
- **CI/CD pipeline**: Automated testing and deployment via GitHub Actions
- **Redis caching**: Cache GET responses for frequently accessed data
- **Update/Delete endpoints**: `PUT /users/<id>` and `DELETE /users/<id>`
- **Pagination links**: Include `next`/`prev` URLs in pagination metadata
- **Request logging middleware**: Structured logging for all API requests
- **API versioning**: URL-based (`/api/v1/users`) or header-based versioning
