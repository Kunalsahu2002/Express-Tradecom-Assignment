"""
Application entry point.

Creates the Flask app via the factory and runs the development server.
For production, use gunicorn instead: gunicorn "app:create_app()"
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
