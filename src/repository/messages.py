from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from models import Messages
from database import session
from schemas import CreateTextMessageExtended, CreateMediaMessageDB
from utilities import MessagesStatus


async def insert_empty_message(sender_id: int, conversation_id: int) -> int:
    async with session() as cursor:
        query = (
            insert(Messages)
            .values(
                sender_id=sender_id,
                conversation_id=conversation_id,
                status=MessagesStatus.CREATED
            )
            .returning(Messages.id)
        )
        message_id = await cursor.execute(query)
        message_id = message_id.scalar()
        await cursor.commit()

        return message_id


async def insert_text_message_to_db(sender_id: int, conversation_id: int, message_data: CreateTextMessageExtended) -> None:
    async with session() as cursor:
        query = (
            insert(Messages)
            .values(
                sender_id=sender_id,
                conversation_id=conversation_id,
                **message_data.model_dump(exclude_none=True)
            )
        )
        await cursor.execute(query)
        await cursor.commit()


async def insert_media_message_to_db(message_id: int, message_data: CreateMediaMessageDB) -> None:
    async with session() as cursor:
        query = (
            update(Messages)
            .filter_by(id=message_id)
            .values(
                updated_at=None,
                **message_data.model_dump(exclude_none=True)
            )
        )
        await cursor.execute(query)
        await cursor.commit()
