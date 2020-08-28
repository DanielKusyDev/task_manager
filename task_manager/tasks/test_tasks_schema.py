import json
from datetime import datetime, timedelta

import marshmallow
import pytest

from task_manager.tasks.schema import EndDateValidationMixin, TaskSchema, UpdateTaskSchema


def test_end_date_validation_mixin():
    mixin = EndDateValidationMixin()
    with pytest.raises(marshmallow.ValidationError):
        data = {"end_date": datetime.utcnow() - timedelta(days=1)}
        mixin.validate_end_date(data)


@pytest.mark.parametrize("excluded_field", ["description", "end_date"])
def test_required_fields_of_task_schema(excluded_field):
    data = {
        "description": "test",
        "end_date": "2020-01-01 12:12:12"
    }
    with pytest.raises(marshmallow.ValidationError):
        del data[excluded_field]
        TaskSchema().loads(json.dumps(data))


def test_task_schema():
    data = json.dumps({
        "description": "desc",
        "end_date": "2021-01-01 10:10:10",
        "slack_webhook_url": "https://example.com"
    })
    loaded_data = TaskSchema().loads(data)
    assert isinstance(loaded_data["created_at"], datetime)
    assert not loaded_data["done"]
    assert not loaded_data.get("_id")
    assert loaded_data.get("slack_webhook_url")


@pytest.mark.parametrize("data, expected", [
    ({}, False),
    ({"description": "desc"}, True),
    ({"end_date": "3000-01-01 10:10:10"}, True),
    ({"done": False}, True)
])
def test_update_task_schema(data, expected):
    schema = UpdateTaskSchema()
    assert bool(schema.loads(json.dumps(data))) == expected
