from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import selectinload

from models import Conversations
from database import session
from schemas import EditConversationDB, CreateEmptyConversation, CreateGroupDB
from utilities import ConversationTypes


async def is_conversation_exists(conversation_id: int) -> bool:
    async with session() as cursor:
        query = (
            select(Conversations.id)
            .filter_by(id=conversation_id)
        )
        result = await cursor.execute(query)
        if result.first():
            return True

        return False


async def select_conversation_type(conversation_id: int) -> ConversationTypes:
    async with session() as cursor:
        query = (
            select(Conversations.type)
            .filter_by(id=conversation_id)
        )
        result = await cursor.execute(query)
        return result.scalar()


async def select_conversation(conversation_obj: CreateEmptyConversation | CreateGroupDB) -> Conversations.id:
    async with session() as cursor:
        query = (
            insert(Conversations).returning(Conversations.id)
            .values(
                **conversation_obj.model_dump(exclude_none=True)
            )
        )
        raw_data = await cursor.execute(query)
        await cursor.commit()
        raw_data = raw_data.scalar()

        return raw_data


async def select_conversation_by_id(conversation_id: int) -> Conversations:
    async with session() as cursor:
        query = (
            select(Conversations)
            .options(selectinload(Conversations.members))
            .filter_by(id=conversation_id)
        )
        result = await cursor.execute(query)
        return result.scalar()


async def select_conversations(conversations_ids: list[int]) -> list[Conversations]:
    async with session() as cursor:
        query = (
            select(Conversations)
            .options(selectinload(Conversations.members))
            .filter(Conversations.id.in_(conversations_ids))
        )
        result = await cursor.execute(query)
        return result.scalars().all()


async def delete_conversation_avatar(conversation_id: int) -> None:
    async with session() as cursor:
        query = (
            update(Conversations)
            .filter_by(id=conversation_id)
            .values(
                avatar_name=None,
                avatar_type=None
            )
        )
        await cursor.execute(query)
        await cursor.commit()


async def update_conversation(conversation_id: int, conversation_obj: EditConversationDB):
    async with session() as cursor:
        query = (
            update(Conversations)
            .filter_by(id=conversation_id)
            .values(**conversation_obj.model_dump(exclude_none=True))
        )
        await cursor.execute(query)
        await cursor.commit()


async def delete_conversation(conversation_id: int) -> None:
    async with session() as cursor:
        query = (
            delete(Conversations)
            .filter_by(id=conversation_id)
        )
        await cursor.execute(query)
        await cursor.commit()
