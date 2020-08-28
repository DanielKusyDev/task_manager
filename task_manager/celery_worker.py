from celery import Celery

from task_manager import settings

celery = Celery("task_manager", broker=settings.CELERY_BROKER_URL)
celery.config_from_object(settings)
