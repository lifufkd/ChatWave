from database import engine, OrmBase
import models


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.create_all)


async def delete_tables():
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.drop_all)

