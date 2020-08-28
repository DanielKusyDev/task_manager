from datetime import datetime

from flask_marshmallow import Schema
from flask_marshmallow.fields import fields
from marshmallow import validates_schema, ValidationError
from marshmallow.validate import Length

from task_manager.slack.schema import WebhookSchema

not_empty = Length(min=1, error="Field may not be empty.")


class EndDateValidationMixin:
    @validates_schema
    def validate_end_date(self, data, *args, **kwargs):
        end_date = data.get("end_date")
        if end_date and end_date <= datetime.utcnow():
            raise ValidationError("Date can't be less than current date", field_name="end_date")
        return data


class TaskSchema(EndDateValidationMixin, Schema):
    _id = fields.Str(dump_only=True, required=True)
    description = fields.Str(required=True, allow_none=False, validate=not_empty)
    end_date = fields.DateTime(required=True)
    created_at = fields.DateTime(missing=datetime.utcnow())
    done = fields.Boolean(missing=False)
    user_id = fields.String()


class UpdateTaskSchema(EndDateValidationMixin, Schema):
    description = fields.Str(allow_none=False, validate=not_empty)
    end_date = fields.DateTime()
    done = fields.Boolean()
