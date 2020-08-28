from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from task_manager import bcrypt, db
from task_manager.slack.schema import WebhookSchema
from task_manager.users.schema import UserSchema

users = Blueprint('users', __name__)
model = db.Model("users")


@users.route("/users", methods=["POST", ])
def registration():
    schema = UserSchema()
    try:
        data = schema.loads(request.data.decode())
        if model.get_one(False, email=data["email"]):
            raise ValidationError("User with given email already exists.")
    except ValidationError as e:
        return jsonify(e.messages), 400
    password = bcrypt.generate_password_hash(data["password"]).decode()
    user_id = model.insert(email=data['email'], password=password, created_at=datetime.utcnow())
    return jsonify({"_id": user_id}), 201


@users.route("/login", methods=["POST"])
def login():
    schema = UserSchema()
    try:
        data = schema.loads(request.data.decode())
    except ValidationError as e:
        return jsonify(e.messages), 400

    user = model.get_one(email=data["email"])
    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        user_id = {"_id": str(user["_id"])}
        access_token = create_access_token(identity=user_id)
        return jsonify({"token": access_token})
    return jsonify({"error": "Invalid username and/or password."})


@users.route("/users/webhook", methods=["POST"])
@jwt_required
def set_slack_webhook():
    schema = WebhookSchema()
    try:
        data = schema.loads(request.data.decode())
    except ValidationError as e:
        return jsonify(e.messages), 400

    user_id = get_jwt_identity()["_id"]
    model.update(_id=ObjectId(user_id), many=False, data=data)
    tasks_model = db.Model("tasks")
    tasks_model.update(user_id=user_id, many=True, data=data)
    return jsonify(request.json)
