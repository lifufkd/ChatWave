from sqlalchemy import select, delete, and_
from models import Conversations, Users, ConversationMembers
from utilities import ConversationMemberRoles
from database import session


async def add_conversation_members_in_db(users_objects: list[Users], conversation_id: int, role: ConversationMemberRoles) -> None:
    async with session() as cursor:
        for user_id in users_objects:
            cursor.add(
                ConversationMembers(
                    user_id=user_id.id,
                    conversation_id=conversation_id,
                    role=role
                )
            )
        await cursor.commit()


async def delete_conversation_members_in_db(conversation_id: int, members_ids: list[int]) -> None:
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


async def get_conversation_member_role_from_db(user_id: int, conversation_id: int) -> ConversationMemberRoles:
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
