import asyncio

from database.postgresql import session, engine, OrmBase
from database.redis import redis_client


async def main():
    async with engine.begin() as con:
        await con.run_sync(OrmBase.metadata.create_all)

print(redis_client.keys("*"))


asyncio.run(main())

