from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from database import redis_client
from repository import create_tables
from routes import (
    authorization_router,
    users_router,
    conversations_router,
    anonymous_users_router,
    messages_router
)
from utilities import FileManager


@asynccontextmanager
async def lifespan(_: FastAPI):
    FileManager().init_folders()
    FastAPICache.init(RedisBackend(redis_client), prefix="chatwave-cache")
    await create_tables()
    yield

app = FastAPI(
    title="ChatWave",
    description="ChatWave - Modern, Simple and Secure REST API for self-hosted messanger",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(authorization_router)

app.include_router(anonymous_users_router)
app.include_router(users_router)

app.include_router(conversations_router)

app.include_router(messages_router)

