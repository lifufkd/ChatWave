import redis
from utilities.config import redis_settings


redis_client = redis.Redis(
    host=redis_settings.REDIS_HOST,
    port=redis_settings.REDIS_PORT,
    db=redis_settings.REDIS_DATABASE,
    username=redis_settings.REDIS_USER,
    password=redis_settings.REDIS_PASSWORD
)
