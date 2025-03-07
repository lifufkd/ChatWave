from fastapi.testclient import TestClient

from models import Users
from factories.users import UserFactory
from constants.users import UsersConstants


async def test_signin(client: TestClient) -> None:
    user: Users = await UserFactory()
    login_data: dict = {
        "username": user.username,
        "password": UsersConstants.DEFAULT_PASSWORD,
    }
    response = client.post("/auth/login", data=login_data)
    tokens: dict = response.json()
    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


async def test_signup(client: TestClient) -> None:
    signup_data = {
        "nickname": "ssqwd",
        "username": "uyiyuiy",
        "password": "fweEFfwefweEW445@",
    }
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201
