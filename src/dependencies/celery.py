from celery import Celery
from celery.schedules import crontab

from utilities import redis_settings

celery_client = Celery(
    "chatwave",
    broker=redis_settings.redis_url,
    backend=redis_settings.redis_url,
    include=['tasks.tasks'],
)

celery_client.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
)


celery_client.conf.beat_schedule = {
    "run-every-hour": {
        "task": "tasks.tasks.sync_users_last_online",
        "schedule": crontab(minute="0", hour="*"),
    },
}
