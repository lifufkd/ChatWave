from sqlalchemy import text

from database import engine, OrmBase, session
from utilities import db_settings
import models # noqa


async def create_schema() -> None:
    async with session() as cursor:
        await cursor.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {db_settings.DB_SCHEMA};")
        )
        await cursor.commit()


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.create_all)


async def delete_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.drop_all)
