"""
User model — SQLAlchemy table definition.

Maps to the 'users' table in the MySQL 'users' database.
Only column definitions and constraints belong here — no business logic.
"""

from app.extensions import db


class User(db.Model):
    """User database model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        """Serialize the User instance to a plain dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
        }

    def __repr__(self):
        return f'<User {self.id}: {self.name}>'
