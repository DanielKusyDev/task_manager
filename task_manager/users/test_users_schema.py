import json
from contextlib import nullcontext

import pytest
from marshmallow import ValidationError

from task_manager.users.schema import UserSchema


@pytest.mark.parametrize("data, context", [
    ({"email": "test@test.com", "password": "passwd"}, nullcontext()),
    ({}, pytest.raises(ValidationError)),
    ({"email": "", "password": "passwd"}, pytest.raises(ValidationError)),
    ({"email": None, "password": "passwd"}, pytest.raises(ValidationError)),
    ({"email": "test@test.com", "password": ""}, pytest.raises(ValidationError)),
    ({"email": "test@test.com", "password": None}, pytest.raises(ValidationError)),
])
def test_user_schema(data, context):
    schema = UserSchema()
    with context:
        schema.loads(json.dumps(data))
