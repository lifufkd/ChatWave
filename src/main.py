from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from database import redis_client
from repository import create_tables, delete_tables
from routes import authorization_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(RedisBackend(redis_client), prefix="chatwave-cache")
    # await delete_tables()  # TODO: Remove after debug
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(authorization_router)



