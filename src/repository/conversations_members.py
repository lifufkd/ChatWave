from sqlalchemy import select, delete, and_, func, update, asc, insert
from models import ConversationMembers
from utilities import ConversationMemberRoles
from database import session


async def insert_members_to_conversation(
        users_ids: list[int],
        conversation_id: int,
        role: ConversationMemberRoles
) -> None:
    async with session() as cursor:
        for user_id in users_ids:
            query = (
                insert(ConversationMembers)
                .values(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    role=role,
                )
            )
            await cursor.execute(query)

        await cursor.commit()


async def delete_conversation_members(conversation_id: int, members_ids: list[int]) -> None:
    async with session() as cursor:
        query = (
            delete(ConversationMembers)
            .filter(
                and_(
                    ConversationMembers.conversation_id == conversation_id,
                    ConversationMembers.user_id.in_(members_ids)
                )
            )
        )
        await cursor.execute(query)
        await cursor.commit()


async def update_conversation_member(conversation_id: int, member_id: int, role: ConversationMemberRoles) -> None:
    async with session() as cursor:
        query = (
            update(ConversationMembers)
            .filter_by(
                conversation_id=conversation_id,
                user_id=member_id
            )
            .values(
                role=role
            )
        )
        await cursor.execute(query)
        await cursor.commit()


async def select_conversation_member_role(user_id: int, conversation_id: int) -> ConversationMemberRoles:
    async with session() as cursor:
        query = (
            select(ConversationMembers.role)
            .filter_by(
                user_id=user_id,
                conversation_id=conversation_id
            )
        )
        result = await cursor.execute(query)
        return result.scalar()


async def select_conversation_members_quantity(conversation_id: int) -> int:
    async with session() as cursor:
        query = (
            select(func.count())
            .select_from(ConversationMembers)
            .filter_by(conversation_id=conversation_id)
        )
        result = await cursor.execute(query)
        return result.scalar()


async def select_conversation_members(conversation_id: int) -> list[ConversationMembers]:
    async with session() as cursor:
        query = (
            select(ConversationMembers)
            .filter_by(conversation_id=conversation_id)
            .order_by(asc(ConversationMembers.joined_at))
        )
        result = await cursor.execute(query)
        return result.scalars().all()


async def select_conversation_admin_members(conversation_id: int) -> list[ConversationMembers]:
    async with session() as cursor:
        query = (
            select(ConversationMembers)
            .filter(
                and_(
                    ConversationMembers.conversation_id == conversation_id,
                    ConversationMembers.role != ConversationMemberRoles.MEMBER
                )
            )
        )
        result = await cursor.execute(query)
        return result.scalars().all()
