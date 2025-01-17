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
