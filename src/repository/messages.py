from sqlalchemy import select, update, insert, and_, func, delete
from sqlalchemy.orm import selectinload

from models import Messages
from database import session
from schemas import CreateTextMessageExtended, CreateMediaMessageDB, UpdateMessage
from utilities import MessagesStatus


async def check_message_is_existed(message_id: int) -> bool:
    async with session() as cursor:
        query = (
            select(Messages.id)
            .filter_by(id=message_id)
        )
        result = await cursor.execute(query)
        if result.first():
            return True

        return False


async def check_messages_is_existed(messages_ids: list[int]) -> bool:
    async with session() as cursor:
        query = (
            select(func.count(Messages.id))
            .filter(Messages.id.in_(messages_ids))
        )
        result = await cursor.execute(query)
        result = result.scalar()
        if result == len(messages_ids):
            return True

        return False


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


async def update_message_in_db(message_id: int, message_data: UpdateMessage) -> None:
    async with session() as cursor:
        query = (
            update(Messages)
            .filter_by(id=message_id)
            .values(content=message_data.content)
        )
        await cursor.execute(query)
        await cursor.commit()


async def get_message_from_db(message_id: int) -> Messages:
    async with session() as cursor:
        query = (
            select(Messages)
            .filter_by(id=message_id)
        )
        result = await cursor.execute(query)
        return result.scalar()


async def get_messages_from_db(messages_ids: list[int]) -> list[Messages]:
    async with session() as cursor:
        query = (
            select(Messages)
            .options(selectinload(Messages.conversation))
            .filter(Messages.id.in_(messages_ids))
        )
        result = await cursor.execute(query)
        return result.scalars()


async def fetch_filtered_messages_from_db(conversation_id: int, limit: int, offset: int) -> list[Messages]:
    async with session() as cursor:
        query = (
            select(Messages)
            .filter(
                and_(
                    Messages.conversation_id == conversation_id,
                    Messages.status != MessagesStatus.CREATED
                )
            )
            .order_by(Messages.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await cursor.execute(query)
        result = result.scalars().all()

        return result


async def search_messages_in_db(conversation_id: int, search_query: str) -> list[Messages]:
    async with session() as cursor:
        query = (
            select(Messages)
            .filter_by(conversation_id=conversation_id)
            .filter(Messages.content.icontains(search_query))
        )
        result = await cursor.execute(query)
        return result.scalars().all()


async def delete_conversation_messages_from_db(conversation_id: int) -> None:
    async with session() as cursor:
        query = (
            delete(Messages)
            .filter_by(conversation_id=conversation_id)
        )
        await cursor.execute(query)
        await cursor.commit()


async def delete_messages_from_db(messages_ids: list[int]) -> None:
    async with session() as cursor:
        query = (
            delete(Messages)
            .filter(Messages.id.in_(messages_ids))
        )
        await cursor.execute(query)
        await cursor.commit()


async def delete_sender_messages(conversation_id: int, members_ids: list[int]) -> None:
    async with session() as cursor:
        query = (
            delete(Messages)
            .filter(
                and_(
                    Messages.conversation_id == conversation_id,
                    Messages.sender_id.in_(members_ids)
                )
            )
        )
        await cursor.execute(query)
        await cursor.commit()
