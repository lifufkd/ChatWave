from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from database import redis_client
from repository import create_tables, delete_tables
from routes import (
    authorization_router,
    users_router,
    conversations_router,
    anonymous_users_router,
    anonymous_conversations_router,
    messages_router
)
from utilities import FileManager


@asynccontextmanager
async def lifespan(_: FastAPI):
    FileManager().init_folders()
    FastAPICache.init(RedisBackend(redis_client), prefix="chatwave-cache")
    # await delete_tables()  # TODO: Remove after debug
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(authorization_router)

app.include_router(users_router)
app.include_router(anonymous_users_router)

app.include_router(anonymous_conversations_router)

app.include_router(conversations_router)

app.include_router(messages_router)
