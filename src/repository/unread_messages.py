from sqlalchemy import select, insert, func, delete

from models import UnreadMessages
from database import session
from schemas import FilterUnreadMessages
from schemas.unread_messages import UnreadMessageExistedDTO, AddUnreadMessagesDB


async def is_unread_messages_exists(filter_conditions: UnreadMessageExistedDTO) -> bool:
    async with session() as cursor:
        query = (
            select(func.count())
            .select_from(UnreadMessages)
            .filter_by(**filter_conditions.model_dump(exclude_none=True))
        )
        raw_data = await cursor.execute(query)
        if raw_data.scalar() > 0:
            return True

        return False


async def select_unread_messages(filter_conditions: FilterUnreadMessages) -> list[UnreadMessages]:
    async with session() as cursor:
        query = (
            select(UnreadMessages)
            .filter_by(**filter_conditions.model_dump(exclude_none=True))
        )
        raw_data = await cursor.execute(query)
        return raw_data.scalars().all()


async def insert_unread_messages(unread_messages_data: AddUnreadMessagesDB) -> None:
    async with session() as cursor:
        for user_id in unread_messages_data.users_ids:
            query = (
                insert(UnreadMessages)
                .values(
                    user_id=user_id,
                    **unread_messages_data.model_dump(exclude_none=True, exclude={"users_ids"})
                )
            )
            await cursor.execute(query)

        await cursor.commit()


async def delete_unread_messages(filter_conditions: FilterUnreadMessages) -> None:
    async with session() as cursor:
        query = (
            delete(UnreadMessages)
            .filter_by(**filter_conditions.model_dump(exclude_none=True))
        )
        await cursor.execute(query)
        await cursor.commit()
