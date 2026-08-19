"""
User service — all business logic for user operations.

This is the ONLY layer that queries models/db. Routes call exactly
one service method per request. Services raise custom exceptions
(NotFoundError, DuplicateError) for error cases — they never return
HTTP status codes or build JSON responses.
"""

import math
import logging

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User
from app.exceptions import NotFoundError, DuplicateError

logger = logging.getLogger(__name__)


class UserService:
    """Service class encapsulating all user business logic."""

    @staticmethod
    def create_user(data):
        """
        Create a new user.

        Args:
            data: Validated dict with 'name', 'email', 'role'.

        Returns:
            Dict representation of the created user.

        Raises:
            DuplicateError: If a user with the same email already exists.
        """
        # Check for existing email (case-insensitive, MySQL default collation)
        existing = User.query.filter(
            User.email == data['email']
        ).first()

        if existing:
            raise DuplicateError('A user with this email already exists.')

        user = User(
            name=data['name'],
            email=data['email'],
            role=data['role'],
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            # Race-condition duplicate: two simultaneous POSTs bypassed the
            # pre-check. The DB-level UNIQUE constraint caught it.
            db.session.rollback()
            raise DuplicateError('A user with this email already exists.')

        logger.info(f'User created: id={user.id}, email={user.email}')
        return user.to_dict()

    @staticmethod
    def get_users(search=None, page=1, limit=10):
        """
        List users with optional search and pagination.

        Args:
            search: Optional substring to match against name or email (case-insensitive).
            page: Page number (1-indexed, default 1).
            limit: Results per page (default 10, capped at 100).

        Returns:
            Dict with 'users', 'total', 'page', 'limit', 'pages'.
        """
        # Cap limit at 100
        limit = min(limit, 100)

        query = User.query

        # Apply search filter if provided
        if search and search.strip():
            search_term = f'%{search.strip()}%'
            query = query.filter(
                db.or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        # Get total count of filtered results
        total = query.count()

        # Calculate total pages
        pages = math.ceil(total / limit) if total > 0 else 1

        # Apply pagination (offset/limit)
        offset = (page - 1) * limit
        users = query.order_by(User.id.asc()).offset(offset).limit(limit).all()

        return {
            'users': [user.to_dict() for user in users],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages,
        }

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a single user by their ID.

        Args:
            user_id: Integer primary key.

        Returns:
            Dict representation of the user.

        Raises:
            NotFoundError: If no user exists with this ID.
        """
        user = db.session.get(User, user_id)

        if user is None:
            raise NotFoundError('User not found')

        return user.to_dict()
