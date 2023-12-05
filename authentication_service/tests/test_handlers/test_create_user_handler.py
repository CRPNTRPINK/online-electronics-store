from fastapi import status



async def test_create_user(client, get_user_from_database):
    user_data = {
        "name": "Baby",
        "surname": "Bone",
        "email": "babybone@gmail.com",
        "password": "Hleb1234567",
        "password_confirm": "Hleb1234567"
    }
    resp = client.post("/user/", json=user_data)
    data_from_resp = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_error(client):
    user_data = {
        "name": "Baby",
        "surname": "Bone",
        "email": "babybone@gmail.com",
        "password": "Hleb1234567",
        "password_confirm": "Hleb1234567"
    }

    user_data_same_email = {
        "name": "ybab",
        "surname": "Enob",
        "email": "babybone@gmail.com",
        "password": "Hleb1234567",
        "password_confirm": "Hleb1234567"
    }
    resp_one = client.post("/user/", json=user_data)
    resp_two = client.post("/user/", json=user_data_same_email)

    assert resp_one.status_code == status.HTTP_200_OK
    assert resp_two.status_code == status.HTTP_409_CONFLICT
    assert (
        "Key (email)=(babybone@gmail.com) already exists." in resp_two.json()["detail"]
    )
