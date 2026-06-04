import re
from uuid import UUID

from fastapi.testclient import TestClient


def _register(
    client: TestClient,
    username: str = "wizard_one",
    password: str = "secret12",
) -> dict:
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": username,
            "password": password,
            "password_confirm": password,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def _auth_headers(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def test_register_and_login(client: TestClient) -> None:
    registered = _register(client, "alpha_mage")
    user_id = registered["id"]

    wrong = client.post(
        "/api/v1/users/login",
        json={"username": "alpha_mage", "password": "wrongpass"},
    )
    assert wrong.status_code == 401

    ok = client.post(
        "/api/v1/users/login",
        json={"username": "alpha_mage", "password": "secret12"},
    )
    assert ok.status_code == 200
    assert ok.json()["id"] == user_id

    profile = client.get("/api/v1/users/me", headers=_auth_headers(user_id))
    assert profile.status_code == 200
    body = profile.json()
    assert body["username"] == "alpha_mage"
    assert body["has_password"] is True


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    _register(client, "dup_user")
    again = client.post(
        "/api/v1/users/register",
        json={
            "username": "dup_user",
            "password": "secret12",
            "password_confirm": "secret12",
        },
    )
    assert again.status_code == 409


def test_register_rejects_password_mismatch(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/register",
        json={
            "username": "mismatch_user",
            "password": "secret12",
            "password_confirm": "other12",
        },
    )
    assert response.status_code == 400


def test_create_game_with_custom_name_and_join_by_name(client: TestClient) -> None:
    host = _register(client, "host_mage")
    guest = _register(client, "guest_mage")
    headers = _auth_headers(host["id"])

    created = client.post(
        "/api/v1/game/new",
        json={"host_user_id": host["id"], "name": "arena42"},
        headers=headers,
    )
    assert created.status_code == 200, created.text
    game = created.json()
    assert game["name"] == "arena42"

    host_join = client.post(
        "/api/v1/game/join",
        json={"user_id": host["id"], "game_ref": "arena42"},
        headers=headers,
    )
    assert host_join.status_code == 200, host_join.text

    guest_join = client.post(
        "/api/v1/game/join",
        json={"user_id": guest["id"], "game_ref": "arena42"},
        headers=_auth_headers(guest["id"]),
    )
    assert guest_join.status_code == 200, guest_join.text
    assert len(guest_join.json()["players"]) == 2


def test_create_game_without_name_uses_default_pattern(client: TestClient) -> None:
    host = _register(client, "auto_host")
    response = client.post(
        "/api/v1/game/new",
        json={"host_user_id": host["id"]},
        headers=_auth_headers(host["id"]),
    )
    assert response.status_code == 200, response.text
    assert re.fullmatch(r"game-\d+", response.json()["name"])


def test_list_games_includes_joinable_game(client: TestClient) -> None:
    host = _register(client, "lister_host")
    headers = _auth_headers(host["id"])
    client.post(
        "/api/v1/game/new",
        json={"host_user_id": host["id"], "name": "listed99"},
        headers=headers,
    )

    listed = client.get("/api/v1/game", headers=headers)
    assert listed.status_code == 200
    names = [item["name"] for item in listed.json()]
    assert "listed99" in names


def test_join_by_uuid_still_works(client: TestClient) -> None:
    host = _register(client, "uuid_host")
    guest = _register(client, "uuid_guest")
    headers = _auth_headers(host["id"])

    created = client.post(
        "/api/v1/game/new",
        json={"host_user_id": host["id"], "name": "uuidroom"},
        headers=headers,
    )
    game_id = created.json()["id"]
    UUID(game_id)

    host_join = client.post(
        "/api/v1/game/join",
        json={"user_id": host["id"], "game_ref": game_id},
        headers=headers,
    )
    assert host_join.status_code == 200, host_join.text

    guest_join = client.post(
        "/api/v1/game/join",
        json={"user_id": guest["id"], "game_ref": game_id},
        headers=_auth_headers(guest["id"]),
    )
    assert guest_join.status_code == 200, guest_join.text
    assert len(guest_join.json()["players"]) == 2
