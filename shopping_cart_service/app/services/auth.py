from uuid import UUID

from fastapi import HTTPException, status

from app.services.services_path import Auth
from app.state import get_http_client


async def get_user_by_id(user_id: UUID):
    params = {'user_id': str(user_id)}
    headers = {
        'accept': 'application/json'
    }

    async with get_http_client().get(Auth.get_user.value, params=params, headers=headers) as response:
        if response.status != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status, detail=await response.json())
        data = await response.json()
        return data
