import json
from contextlib import nullcontext

import pytest
from marshmallow import ValidationError

from task_manager.slack import messages
from task_manager.slack.schema import WebhookSchema
from task_manager.utils import decrypt


@pytest.fixture
def slack_message():
    return messages.SlackMessage()


def test_slack_message_header(slack_message):
    header = slack_message.get_header("test123")
    assert header["text"]["text"] == "test123"
    assert header["type"] == "header"


def test_slack_message_field_section(slack_message):
    section = slack_message.get_field_section(["field1", "field2"])
    fields = section["fields"]
    assert len(fields) == 2
    assert fields[0]["text"] == "field1"
    assert fields[1]["text"] == "field2"


def test_slack_message_text_section(slack_message):
    section = slack_message.get_text_section("test123")
    assert section["text"]["text"] == "test123"
    assert section["type"] == "section"


def test_slack_message_divider(slack_message):
    divider = slack_message.get_divider()
    assert len(divider.keys()) == 1
    assert divider["type"] == "divider"


@pytest.mark.parametrize("fn", [
    messages.get_new_task_slack_message, messages.get_slack_reminder_message
])
def test_notifications(fn):
    description = "Test Description"
    end_date = "2020-01-01 01:01:01"
    notification = fn(description, end_date)
    assert end_date in notification
    assert description in notification
    assert isinstance(notification, str)
    assert json.loads(notification).get("blocks")


@pytest.mark.parametrize("url, context", [
    ("https://example.com", nullcontext()),
    ("......", pytest.raises(ValidationError)),
    ("example", pytest.raises(ValidationError)),
    (None, pytest.raises(ValidationError)),
])
def test_webhook_schema_validation(url, context):
    schema = WebhookSchema()
    with context:
        data = json.dumps({"slack_webhook_url": url})
        schema.loads(data)


def test_webhook_schema_url_encryption():
    url = 'https://example.com'
    json_string = json.dumps({"slack_webhook_url": url})
    data = WebhookSchema().loads(json_string)
    assert decrypt(data["slack_webhook_url"]) == url
