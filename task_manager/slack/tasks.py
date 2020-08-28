import logging
from datetime import datetime

import requests

from task_manager import db, settings, celery
from task_manager.slack.messages import get_slack_reminder_message
from task_manager.utils import decrypt

logger = logging.Logger(__name__)


def send_slack_notifications(tasks):
    for task in tasks:
        webhook = decrypt(task["slack_webhook_url"])
        message = get_slack_reminder_message(task["description"], task["end_date"])
        requests.post(webhook, message)


@celery.task(name="check_for_slack_notification")
def check_for_slack_notification():
    logger.info("Checking for notifications...")
    hours_to_end_projection = {"$divide": [{"$subtract": ["$end_date", datetime.utcnow()]}, 3600000]}
    pipeline = db.AggregationPipeline()
    pipeline.add_match(slack_webhook_url={"$exists": True}, done=False)
    pipeline.add_projection(hours_to_end=hours_to_end_projection, slack_webhook_url=1, description=1, end_date=1)
    pipeline.add_match(hours_to_end={"$lte": settings.HOURS_BEFORE_SLACK_NOTIFICATION})
    tasks = db.Model("tasks").aggregate(pipeline.pipeline)
    send_slack_notifications(tasks)
