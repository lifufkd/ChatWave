from datetime import datetime
from sqlalchemy import select, insert, update, text
from sqlalchemy.orm import selectinload

from models import Users, Conversations
from database import session
from schemas import AuthorizeUser, CreateUserExtended, UpdateUserExtended, UserOnline, SearchUser


async def check_user_is_existed(user_id: int) -> bool:
    async with session() as cursor:
        query = (
            select(Users.id)
            .filter_by(id=user_id)
        )
        result = await cursor.execute(query)
        if result.first():
            return True

        return False


async def get_user_by_username_from_db(user_data: AuthorizeUser) -> tuple[int, str]:
    async with session() as cursor:
        query = (
            select(Users.id, Users.password_hash)
            .filter_by(username=user_data.username)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.first()

        return raw_data


async def insert_user_in_db(user_data: CreateUserExtended) -> None:
    async with session() as cursor:
        query = (
            insert(Users)
            .values(**user_data.model_dump(exclude={"password"}))
        )
        await cursor.execute(query)
        await cursor.commit()


async def get_user_from_db(user_id: int) -> Users:
    async with session() as cursor:
        query = (
            select(Users)
            .options(selectinload(Users.conversations).selectinload(Conversations.members))
            .filter_by(id=user_id)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalar()

        return raw_data


async def get_users_from_db(users_ids: list[int]) -> list[Users]:
    async with session() as cursor:
        query = (
            select(Users)
            .options(selectinload(Users.conversations).selectinload(Conversations.members))
            .filter(Users.id.in_(users_ids))
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalars().all()

        return raw_data


async def get_users_by_nickname_from_db(search_params: SearchUser) -> list[Users]:

    async def query_builder():
        if search_params.limit == 0:
            _query = (
                select(Users)
                .filter(Users.nickname.icontains(search_params.nickname))
            )
        else:
            _query = (
                select(Users)
                .filter(Users.nickname.icontains(search_params.nickname))
                .limit(search_params.limit)
            )

        return _query

    async with session() as cursor:
        query = await query_builder()
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalars().all()

        return raw_data


async def update_user_in_db(user_id: int, user_data: UpdateUserExtended) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(**user_data.model_dump(exclude_none=True, exclude={"password"}))
        )
        await cursor.execute(query)
        await cursor.commit()


async def delete_user_avatar_in_db(user_id: int) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(
                avatar_name=None,
                avatar_type=None
            )
        )
        await cursor.execute(query)
        await cursor.commit()


async def update_user_last_online_in_db(user_id: int) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(last_online=text("TIMEZONE('utc', now())"), updated_at=text("updated_at"))
        )
        await cursor.execute(query)
        await cursor.commit()


async def get_users_online_from_db(users: UserOnline) -> list[tuple[int, datetime]]:
    async with session() as cursor:
        query = (
            select(Users.id, Users.last_online)
            .filter(Users.id.in_(users.users_ids))
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.all()

        return raw_data