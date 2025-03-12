import pytest
from fastapi.testclient import TestClient

from models import Users
from factories.users import UserFactory
from conftest import client
from utilities import JWT
from repository.users import delete_user


@pytest.fixture(scope='function')
async def authorized_test_client(client: TestClient):
    user: Users = await UserFactory()
    access_token = JWT.create_token(
        {
            "id": user.id,
        }
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    yield {"headers": headers, "user_id": user.id}

    await delete_user(user.id)
