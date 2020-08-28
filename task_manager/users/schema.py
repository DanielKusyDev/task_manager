from flask_marshmallow import Schema
from flask_marshmallow.fields import fields
from marshmallow.validate import Length

not_empty = Length(min=1, error="Field may not be empty.")


class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=not_empty, allow_none=False)
