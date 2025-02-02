from datetime import datetime
from sqlalchemy import select, insert, update, text, delete, func
from sqlalchemy.orm import selectinload

from models import Users, Conversations
from database import session
from schemas import CreateUserDB, UpdateUserDB


async def is_user_exists(user_id: int) -> bool:
    async with session() as cursor:
        query = (
            select(Users.id)
            .filter_by(id=user_id)
        )
        result = await cursor.execute(query)
        if result.first():
            return True

        return False


async def fetch_user_credentials_by_username(username: str) -> tuple[int, str]:
    async with session() as cursor:
        query = (
            select(Users.id, Users.password_hash)
            .filter_by(username=username)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.first()

        return raw_data


async def create_user_in_db(user_data: CreateUserDB) -> None:
    async with session() as cursor:
        query = (
            insert(Users)
            .values(**user_data.model_dump())
        )
        await cursor.execute(query)
        await cursor.commit()


async def fetch_user_from_db(user_id: int) -> Users:
    async with session() as cursor:
        query = (
            select(Users)
            .options(selectinload(Users.conversations).selectinload(Conversations.members))
            .filter_by(id=user_id)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalar()

        return raw_data


async def fetch_users_from_db(users_ids: list[int]) -> list[Users]:
    async with session() as cursor:
        query = (
            select(Users)
            .filter(Users.id.in_(users_ids))
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalars().all()

        return raw_data


async def search_users_in_db(search_query: str, limit: int | None) -> list[Users]:

    async def query_builder():
        if limit is None:
            _query = (
                select(Users)
                .filter(Users.nickname.icontains(search_query))
            )
        else:
            _query = (
                select(Users)
                .filter(Users.nickname.icontains(search_query))
                .limit(limit)
            )

        return _query

    async with session() as cursor:
        query = await query_builder()
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalars().all()

        return raw_data


async def update_user_in_db(user_id: int, user_data: UpdateUserDB) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(**user_data.model_dump(exclude_none=True))
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


async def update_users_last_online(users: list[dict]) -> None:
    async with session() as cursor:
        for user in users:
            query = (
                update(Users)
                .filter_by(id=user["user_id"])
                .values(
                    last_online=user["last_online"],
                    updated_at=text("updated_at")
                )
            )
            await cursor.execute(query)

        await cursor.commit()


async def get_users_last_online_from_db(users_ids: list[int]) -> list[tuple[int, datetime]]:
    async with session() as cursor:
        query = (
            select(Users.id, Users.last_online)
            .filter(Users.id.in_(users_ids))
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.all()

        return raw_data


async def delete_user_from_db(user_id: int):
    async with session() as cursor:
        query = (
            delete(Users)
            .filter_by(id=user_id)
        )
        await cursor.execute(query)
        await cursor.commit()
