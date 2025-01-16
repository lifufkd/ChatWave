from datetime import datetime
from sqlalchemy import select, insert, update, text

from models import Users
from database import session
from schemas import AuthorizeUser, CreateUserExtended, UpdateUserExtended, UserOnline, SearchUser


async def authorize_user(user_data: AuthorizeUser) -> bool:
    async with session() as cursor:
        query = (
            select(Users.id, Users.password_hash)
            .filter_by(username=user_data.username)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.first()
        if not raw_data:
            return False

        user_data.id = raw_data[0]
        user_data.password_hash = raw_data[1]

        return True


async def register_user(user_data: CreateUserExtended) -> None:
    async with session() as cursor:
        query = (
            insert(Users)
            .values(**user_data.model_dump(exclude={"password"}))
        )
        await cursor.execute(query)
        await cursor.commit()


async def get_private_user(user_id: int) -> Users:
    async with session() as cursor:
        query = (
            select(Users)
            .filter_by(id=user_id)
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalar()

        return raw_data


async def get_public_users(search_params: SearchUser) -> list[Users]:

    def query_builder():
        if search_params.ids is not None:
            _query = (
                select(Users)
                .filter(Users.id.in_(search_params.ids))
            )
            return _query
        elif search_params.nickname is not None:
            if search_params.limit == 0:
                _query = (
                    select(Users)
                    .filter(Users.nickname.like(search_params.nickname))
                )
            else:
                _query = (
                    select(Users)
                    .filter(Users.nickname.like(search_params.nickname))
                    .limit(search_params.limit)
                )

            return _query

    async with session() as cursor:
        query = query_builder()
        raw_data = await cursor.execute(query)
        raw_data = raw_data.scalars().all()

        return raw_data


async def update_user(user_id: int, user_data: UpdateUserExtended) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(**user_data.model_dump(exclude_none=True, exclude={"password"}))
        )
        await cursor.execute(query)
        await cursor.commit()


async def update_user_last_online_in_db(user_id: int) -> None:
    async with session() as cursor:
        query = (
            update(Users)
            .filter_by(id=user_id)
            .values(last_online=text("TIMEZONE('utc', now())"))
        )
        await cursor.execute(query)
        await cursor.commit()


async def get_users_online(users: UserOnline) -> list[tuple[int, datetime]]:
    async with session() as cursor:
        query = (
            select(Users.id, Users.last_online)
            .filter(Users.id.in_(users.users_ids))
        )
        raw_data = await cursor.execute(query)
        raw_data = raw_data.all()

        return raw_data

