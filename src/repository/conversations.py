from sqlalchemy import select, update

from models import Conversations, Users
from database import session


async def add_conversation_in_db(conversation_obj: Conversations):
    async with session() as cursor:
        cursor.add(conversation_obj)
        await cursor.commit()
        await cursor.refresh(conversation_obj)


async def add_members_to_conversation_in_db(conversation_obj: Conversations, members: list[Users]):
    async with session() as cursor:
        conversation_obj.members.extend(members)
        cursor.add(conversation_obj)

        await cursor.commit()
        await cursor.refresh(conversation_obj)
