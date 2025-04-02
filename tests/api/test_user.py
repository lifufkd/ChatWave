import pytest
import io
from fastapi.testclient import TestClient
from contextlib import nullcontext as does_not_raise

from fixtures.users_fixtures import create_random_users, create_users, upload_avatar
from fixtures.authorization_fixtures import authorized_test_client
from utilities import ImageCorrupted, FIleToBig, InvalidFileType, FileNotFound


async def test_get_current_user(client: TestClient, authorized_test_client):
    response = client.get("/users/me", headers=authorized_test_client["headers"])
    assert response.status_code == 200


async def test_get_users(client: TestClient, create_random_users):
    query_params = dict()
    query_params["users_ids"] = list(create_random_users)
    response = client.get("/users", params=query_params)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize(
    "search_query, search_limit, expected_status_code, expected_quantity",
    [
        ("a", None, 422, 0),
        ("Ryan", None, 200, 2),
        ("Mike", None, 200, 1),
        ("Ryan", 1, 200, 1),
    ],
)
async def test_search_users(client: TestClient, create_users, search_query, search_limit, expected_status_code, expected_quantity):
    query_params = {
        "search_query": search_query
    }
    if search_limit is not None:
        query_params.update({"limit": search_limit})
    response = client.get("/users/search", params=query_params)
    assert response.status_code == expected_status_code
    if response.status_code == 200:
        assert isinstance(response.json(), list)
        assert len(response.json()) == expected_quantity


async def test_get_users_last_online(client: TestClient, authorized_test_client):
    response = client.get("/users/online", headers=authorized_test_client["headers"])

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


async def test_get_current_user_unread_messages(client: TestClient, authorized_test_client):
    response = client.get("/users/messages/unread", headers=authorized_test_client["headers"])

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


@pytest.mark.parametrize(
    "request_body, expected_status_code",
    [
        ({"nickname": "123"}, 204),
        ({"nickname": "12"}, 422),
        ({"password": "wejfkeJKHN5("}, 204),
        ({"password": "12345678"}, 422),
        ({"password": "123456"}, 422),
        ({"birthday": "1999-11-11"}, 204),
        ({"birthday": "11-11-1999"}, 422),
        ({"birthday": "11.11.1999"}, 422),
        ({"birthday": "1999.11.11"}, 422),
        ({"bio": "fewfwefw"}, 204),
        ({}, 422),
    ]
)
async def test_update_current_user(client: TestClient, authorized_test_client, request_body, expected_status_code):
    response = client.patch("/users/me", headers=authorized_test_client["headers"], json=request_body)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "file, file_type, expected_status_code, exception",
    [
        ("tests/media/users_avatars/valid.jpg", {"name": "avatar.jpg", "type": "image/jpeg"}, 204, does_not_raise()),
        ("tests/media/users_avatars/invalid.jpg", {"name": "avatar.jpg", "type": "image/jpeg"}, 422, pytest.raises(ImageCorrupted)),
        ("tests/media/users_avatars/oversized.jpg", {"name": "avatar.jpg", "type": "image/jpeg"}, 422, pytest.raises(FIleToBig)),
        ("tests/media/users_avatars/text.txt", {"name": "text.txt", "type": "text/plane"}, 422, pytest.raises(InvalidFileType)),
    ]
)
async def test_update_current_user_avatar(client: TestClient, authorized_test_client, file, file_type, expected_status_code, exception):
    file_data = io.FileIO(file, "rb")
    files = {"avatar": (file_type["name"], file_data, file_type["type"])}
    with exception:
        response = client.put("/users/me/avatar", headers=authorized_test_client["headers"], files=files)
        assert response.status_code == expected_status_code


async def test_get_not_existed_user_avatar(client: TestClient, authorized_test_client):
    with pytest.raises(FileNotFound):
        client.get(f"/users/{authorized_test_client['user_id']}/avatar")


async def test_get_existed_user_avatar(client: TestClient, upload_avatar):
    response = client.get(f"/users/{upload_avatar}/avatar")
    assert response.status_code == 200


@pytest.mark.skip
async def test_get_not_existed_users_avatars(client: TestClient, authorized_test_client):
    result = client.get(f"/users/avatars", params={"users_ids": [authorized_test_client]})


@pytest.mark.skip
async def test_get_existed_users_avatars(client: TestClient, upload_avatar):
    response = client.get(f"/users/avatars", params={"users_ids": upload_avatar})
    assert response.status_code == 200


async def test_delete_not_existed_current_user_avatar(client: TestClient, authorized_test_client):
    with pytest.raises(FileNotFound):
        client.delete("/users/me/avatar", headers=authorized_test_client["headers"])


async def test_delete_existed_current_user_avatar(client: TestClient, authorized_test_client, upload_avatar):
    client.delete("/users/me/avatar", headers=authorized_test_client["headers"])


async def test_delete_user(client: TestClient, authorized_test_client):
    response = client.delete("/users/me", headers=authorized_test_client["headers"])
    assert response.status_code == 202
