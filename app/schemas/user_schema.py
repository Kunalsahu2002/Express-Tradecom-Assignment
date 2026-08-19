"""
User schema — Marshmallow validation.

Defines and enforces field-level rules for user input.
This schema never touches the database — it only validates/deserializes
incoming request data before it reaches the service layer.
"""

from marshmallow import Schema, fields, validate, pre_load


class UserSchema(Schema):
    """Schema for validating user creation input."""

    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'Missing data for required field.',
            'null': 'Field may not be null.',
        },
    )
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'Missing data for required field.',
            'null': 'Field may not be null.',
            'invalid': 'Not a valid email address.',
        },
    )
    role = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            'required': 'Missing data for required field.',
            'null': 'Field may not be null.',
        },
    )

    @pre_load
    def strip_whitespace(self, data, **kwargs):
        """
        Strip leading/trailing whitespace from string fields.

        Whitespace-only values become empty strings, which will then
        fail the Length(min=1) validation — treating them as missing.
        """
        for field_name in ('name', 'email', 'role'):
            value = data.get(field_name)
            if isinstance(value, str):
                data[field_name] = value.strip()
        return data
