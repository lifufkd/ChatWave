from fastapi.testclient import TestClient

from models import Users
from factories.users import UserFactory
from fixtures.authorization import set_auth_token


async def test_get_current_user(client: TestClient):
    user: Users = await UserFactory()
    authorized_test_client = set_auth_token(client=client, user_id=user.id)
    response = authorized_test_client.get("/users/me")
    assert response.status_code == 200
