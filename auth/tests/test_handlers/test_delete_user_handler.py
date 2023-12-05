import uuid


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Baby_del",
        "surname": "Bone_del",
        "email": "babybonedel@gmail.com",
        "is_active": True,
        "password": "Hleb1234567",
    }
    await create_user_in_database(**user_data)
    resp = client.delete(f'/user/?user_id={user_data["user_id"]}')
    resp_json = resp.json()
    assert resp.status_code == 200
    assert resp_json == {"user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = users_from_db[0]
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert str(user_from_db["user_id"]) == resp_json["user_id"]
