import asyncio
import asyncpg

from .handlers import handle_unread_messages_changes, handle_recipients_change
from utilities import db_settings


async def setup_unread_messages_changes_listener():
    asyncpg_engine = await asyncpg.connect(db_settings.asyncpg_postgresql_url)
    await asyncpg_engine.add_listener(
        "unread_messages_changes", lambda _, __, ___, payload: asyncio.create_task(handle_unread_messages_changes(payload))
    )
    while True:
        await asyncio.sleep(1)


async def setup_recipients_change_listener():
    asyncpg_engine = await asyncpg.connect(db_settings.asyncpg_postgresql_url)
    await asyncpg_engine.add_listener(
        "recipients_change", lambda _, __, ___, payload: asyncio.create_task(handle_recipients_change(payload))
    )
    while True:
        await asyncio.sleep(1)
