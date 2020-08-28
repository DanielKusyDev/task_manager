from celery.schedules import crontab

from task_manager.local_settings import *

JWT_TOKEN_LOCATION = "headers"
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
HOURS_BEFORE_SLACK_NOTIFICATION = 5
MONGO_DBNAME = 'task_manager'
DEFAULT_PAGE_SIZE = 100
SWAGGER_URL = '/swagger'

JWT_ACCESS_TOKEN_EXPIRES = 60 * 3600
CELERY_IMPORTS = ('task_manager.slack.tasks',)

CELERYBEAT_SCHEDULE = {
    'check_for_slack_notification': {
        'task': 'check_for_slack_notification',
        'schedule': crontab(minute=0, hour='*/3')
    },

}
