import time

import pytest
import models # noqa
from repository import create_schema
from database import OrmBase, engine
from database import session as session_factory


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    await create_schema()
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(OrmBase.metadata.drop_all)


@pytest.fixture(scope='function')
async def get_db_session():
    async with session_factory() as session:
        yield session
