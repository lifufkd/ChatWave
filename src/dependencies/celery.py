from celery import Celery

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
