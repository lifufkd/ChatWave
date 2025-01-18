from sqlalchemy import select
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


async def get_conversation_member_role_from_db(user_id: int, conversation_id: int):
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
