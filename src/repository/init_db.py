from database import engine, OrmBase
import models # noqa


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.create_all)


async def delete_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.drop_all)
