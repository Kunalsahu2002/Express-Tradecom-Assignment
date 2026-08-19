"""
Custom exception classes for domain-level errors.

These exceptions are raised by the service layer and caught by
centralized error handlers registered in the app factory.
Routes never catch these directly — they propagate up to the handlers.
"""


class ValidationError(Exception):
    """Raised when input validation fails at the business-logic level."""

    def __init__(self, message='Validation error'):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message='Resource not found'):
        self.message = message
        super().__init__(self.message)


class DuplicateError(Exception):
    """Raised when a unique constraint would be violated (e.g. duplicate email)."""

    def __init__(self, message='Resource already exists'):
        self.message = message
        super().__init__(self.message)
