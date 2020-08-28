import json

import requests
from bson import ObjectId, json_util
from flask import Blueprint, request, jsonify, Response, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from task_manager import db, settings
from task_manager.slack.messages import get_new_task_slack_message
from task_manager.tasks.schema import TaskSchema, UpdateTaskSchema
from task_manager.tasks import utils
from task_manager.utils import decrypt, Paginator

tasks = Blueprint('tasks', __name__)
tasks_model = db.Model("tasks")


@tasks.route("/tasks", methods=["POST"])
@jwt_required
def create_task():
    user_model = db.Model("users")
    schema = TaskSchema()
    logged_user_id = get_jwt_identity()["_id"]
    user = user_model.get_one(raise_404=True, _id=ObjectId(logged_user_id))
    raw_data = {
        "user_id": logged_user_id,
        **request.json
    }
    try:
        data = schema.load(raw_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    if webhook := user.get("slack_webhook_url"):
        data["slack_webhook_url"] = webhook
        webhook = decrypt(webhook)
        slack_message = get_new_task_slack_message(raw_data["description"], raw_data["end_date"])
        requests.post(webhook, slack_message)
    task_id = tasks_model.insert(many=False, **data)

    return jsonify({"_id": task_id}), 201


@tasks.route("/tasks/<string:task_id>", methods=["GET"])
@jwt_required
@utils.task_owner_only
def get_task_details(task_id):
    schema = TaskSchema()
    task = tasks_model.get_one(raise_404=True, _id=ObjectId(task_id))
    task = json.loads(schema.dumps(task))
    return jsonify(task)


@tasks.route("/tasks", methods=["GET"])
@jwt_required
def list_tasks():
    schema = TaskSchema(many=True)
    paginator = Paginator()
    cursor = tasks_model.all()
    task_list = paginator.get_paginated_documents(cursor)
    results = json.loads(schema.dumps(list(task_list)))
    data = {
        "total": tasks_model.count(),
        "results": results
    }
    data.update(paginator.get_navigation(data["total"]))
    return jsonify(data)


@tasks.route("/tasks/<string:task_id>", methods=["PUT"])
@jwt_required
@utils.task_owner_only
def update_task(task_id):
    schema = UpdateTaskSchema()
    _id = ObjectId(task_id)
    try:
        data = schema.loads(request.data.decode())
    except ValidationError as e:
        return jsonify(e.messages), 400
    tasks_model.get_one(raise_404=True, _id=_id)
    tasks_model.update(data=data, many=False, _id=_id)
    task = tasks_model.get_one(raise_404=False, _id=_id)
    task = json.loads(schema.dumps(task))
    return jsonify(task)


@tasks.route("/tasks/<string:task_id>", methods=["DELETE"])
@jwt_required
@utils.task_owner_only
def delete_task(task_id):
    tasks_model.delete(_id=ObjectId(task_id))
    return Response(status=200)


@tasks.route("/tasks/reports")
@jwt_required
def create_reports():
    period = request.args.get("period", "week")
    service_mapping = {
        "week": utils.WeeklyReportService,
        "month": utils.MonthlyReportService,
        "year": utils.YearlyReportService
    }
    service = service_mapping[period]()
    reports = service.generate_reports()
    return jsonify(reports)
