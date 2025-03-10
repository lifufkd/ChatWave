import pytest
import io
from fastapi.testclient import TestClient

from models import Users
from factories.users import UserFactory
from repository.users import delete_user
from fixtures.authorization import authorized_test_client


@pytest.fixture(scope='function')
async def create_random_users():
    users_ids = list()
    for _ in range(3):
        user_obj: Users = await UserFactory()
        users_ids.append(user_obj.id)

    yield users_ids

    for user_id in users_ids:
        await delete_user(user_id)


@pytest.fixture(scope='function')
async def create_users():
    users = list()
    for user_nickname in ["Jason", "Ryan", "Mike", "Jake", "Ryan Gosling"]:
        user: Users = await UserFactory(nickname=user_nickname)
        users.append({"id": user.id, "nickname": user.nickname})

    yield users

    for user_id in users:
        await delete_user(user_id["id"])


@pytest.fixture(scope='function')
async def upload_avatar(client: TestClient, authorized_test_client, file_name: str = "tests/media/users_avatars/valid.jpg") -> int:
    file_data = io.FileIO(file_name, "rb")
    files = {"avatar": ("avatar.jpg", file_data, "image/jpeg")}
    response = client.put("/users/me/avatar", headers=authorized_test_client["headers"], files=files)
    assert response.status_code == 204

    return authorized_test_client["user_id"]
