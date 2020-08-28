from flask_marshmallow import Schema
from flask_marshmallow.fields import fields
from marshmallow import post_load

from task_manager import utils


class WebhookSchema(Schema):
    slack_webhook_url = fields.Url(required=True, allow_none=False)

    @post_load
    def encrypt_url(self, data, *args, **kwargs):
        data["slack_webhook_url"] = utils.encrypt(data["slack_webhook_url"])
        return data
