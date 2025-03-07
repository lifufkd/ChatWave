import asyncio
import pytest
from fastapi.testclient import TestClient

import models # noqa
from repository import create_schema
from utilities import generic_settings, AppModes
from database import OrmBase, engine
from database import session as session_factory
from main import app
from factories.users import UserFactory


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    assert generic_settings.MODE == AppModes.TESTING.value
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


@pytest.fixture(autouse=True)
def set_session_for_factories(get_db_session):
    UserFactory._meta.sqlalchemy_session = get_db_session


@pytest.fixture(scope='function')
def client() -> [TestClient, None, None]:
    return TestClient(app)

