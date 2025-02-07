from sqlalchemy import select, update, insert, and_, delete, text
from sqlalchemy.orm import selectinload

from models import Messages
from database import session
from schemas import CreateTextMessageDB, CreateMediaMessageDB
from utilities import MessagesStatus


async def is_message_exists(message_id: int) -> bool:
    async with session() as cursor:
        query = (
            select(Messages.id)
            .filter_by(id=message_id)
        )
        result = await cursor.execute(query)
        if result.first():
            return True

        return False


async def update_message_status(message_id: int, status: MessagesStatus) -> None:
    async with session() as cursor:
        query = (
            update(Messages)
            .filter_by(id=message_id)
            .values(
                status=status,
                updated_at=text("updated_at"),
            )
        )
        await cursor.execute(query)
        await cursor.commit()


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


async def insert_text_message(sender_id: int, conversation_id: int, message_data: CreateTextMessageDB) -> int:
    async with session() as cursor:
        query = (
            insert(Messages).returning(Messages.id)
            .values(
                sender_id=sender_id,
                conversation_id=conversation_id,
                **message_data.model_dump(exclude_none=True)
            )
        )
        raw_data = await cursor.execute(query)
        await cursor.commit()

        return raw_data.scalar()


async def insert_media_message(message_id: int, message_data: CreateMediaMessageDB) -> None:
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


async def update_message(message_id: int, content: str) -> None:
    async with session() as cursor:
        query = (
            update(Messages)
            .filter_by(id=message_id)
            .values(content=content)
        )
        await cursor.execute(query)
        await cursor.commit()


async def select_message(message_id: int) -> Messages:
    async with session() as cursor:
        query = (
            select(Messages)
            .filter_by(id=message_id)
        )
        result = await cursor.execute(query)
        return result.scalar()


async def select_messages(messages_ids: list[int]) -> list[Messages]:
    async with session() as cursor:
        query = (
            select(Messages)
            .options(selectinload(Messages.conversation))
            .filter(Messages.id.in_(messages_ids))
        )
        result = await cursor.execute(query)
        return result.scalars()


async def select_message_status(message_id: int) -> MessagesStatus:
    async with session() as cursor:
        query = (
            select(Messages.status)
            .filter_by(id=message_id)
        )
        raw_data = await cursor.execute(query)
        return raw_data.scalar()


async def select_filtered_messages(conversation_id: int, limit: int, offset: int) -> list[Messages]:
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


async def select_messages_by_content(conversation_id: int, search_query: str, limit: int) -> list[Messages]:
    async with session() as cursor:
        query = (
            select(Messages)
            .filter_by(conversation_id=conversation_id)
            .filter(Messages.content.icontains(search_query))
            .limit(limit)
        )
        result = await cursor.execute(query)
        return result.scalars().all()


async def delete_conversation_messages(conversation_id: int) -> None:
    async with session() as cursor:
        query = (
            delete(Messages)
            .filter_by(conversation_id=conversation_id)
        )
        await cursor.execute(query)
        await cursor.commit()


async def delete_messages(messages_ids: list[int]) -> None:
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
