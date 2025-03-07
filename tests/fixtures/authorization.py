import pytest
from fastapi.testclient import TestClient

from conftest import client
from models import Users
from factories.users import UserFactory
from utilities import JWT


def set_auth_token(client: TestClient, user_id: int) -> TestClient:
    access_token = JWT.create_token(
        {
            "id": user_id,
        }
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    client.headers.update(headers)
    return client
