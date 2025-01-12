from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from database import redis_client
from repository import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(RedisBackend(redis_client), prefix="chatwave-cache")
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

# app.include_router()

# if __name__ == "__main__":
#     pass

