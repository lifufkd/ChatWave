from sqlalchemy import select, insert

from models import Users
from database import session
from schemas import AuthorizeUser, CreateUserExtended


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
            .values(
                nickname=user_data.nickname,
                username=user_data.username,
                password_hash=user_data.password_hash
            )
        )
        await cursor.execute(query)
        await cursor.commit()

