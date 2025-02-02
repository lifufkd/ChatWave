import asyncio
from datetime import datetime

from dependencies import celery_client, redis_client
from repository import update_users_last_online


@celery_client.task
def sync_users_last_online():
    loop = asyncio.get_event_loop()

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_sync_users_last_online())


async def _sync_users_last_online():
    users_last_online = list()

    keys = await redis_client.keys("user:last_online:*")
    for key in keys:
        user_id = int(key.decode().split(":")[-1])
        raw_last_online = await redis_client.get(key)
        last_online = datetime.strptime(raw_last_online.decode(), "%Y-%m-%d %H:%M:%S")
        users_last_online.append(
            {
                "user_id": user_id,
                "last_online": last_online
            }
        )

    await update_users_last_online(users_last_online)


