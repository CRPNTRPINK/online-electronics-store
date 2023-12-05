import uuid

from fastapi import status


async def test_update_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby_get",
        "surname": "Bone_get",
        "email": "babyboneget@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }

    await create_user_in_database(**user_data)
    changed_data = {
        "name": "justbaby",
    }
    user_data["name"] = changed_data["name"]

    resp = client.put(f'/user/?user_id={user_data["user_id"]}', json=changed_data)
    resp_json = resp.json()
    user_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = user_from_db[0]
    user_data["user_id"] = str(user_data["user_id"])
    del user_data['password']

    assert resp.status_code == 200
    assert user_data == resp_json
    assert str(user_from_db["user_id"]) == user_data["user_id"]
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] == user_data["is_active"]


async def test_update_user_duplicate_email(
    client, create_user_in_database, get_user_from_database
):
    another_user = {
        "user_id": uuid.uuid4(),
        "name": "John",
        "surname": "Doe",
        "email": "JohnDoe@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby",
        "surname": "Bone",
        "email": "babybone@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }

    await create_user_in_database(**another_user)
    await create_user_in_database(**user_data)

    changed_data = {
        "email": "JohnDoe@gmail.com",
    }
    user_data["email"] = changed_data["email"]
    resp = client.put(f'/user/?user_id={user_data["user_id"]}', json=changed_data)

    assert resp.status_code == status.HTTP_409_CONFLICT


async def test_update_user_empty_body(
    client, create_user_in_database, get_user_from_database
):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby",
        "surname": "Bone",
        "email": "babybone@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }

    await create_user_in_database(**user_data)

    changed_data = {}
    resp = client.put(f'/user/?user_id={user_data["user_id"]}', json=changed_data)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_user_not_found(
    client, create_user_in_database, get_user_from_database
):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby",
        "surname": "Bone",
        "email": "babybone@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }

    await create_user_in_database(**user_data)

    changed_data = {"email": "hello@gmail.com"}
    user_id = uuid.uuid4()
    resp = client.put(f"/user/?user_id={user_id}", json=changed_data)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
