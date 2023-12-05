import uuid


async def test_get_user_by_id(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby_get",
        "surname": "Bone_get",
        "email": "babyboneget@gmail.com",
        "is_active": True,
        "password": "Hleb1234567"
    }

    await create_user_in_database(**user_data)
    resp = client.get(f'/user/?user_id={user_data["user_id"]}')
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
