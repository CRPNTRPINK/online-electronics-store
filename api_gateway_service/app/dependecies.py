from typing import Annotated, Optional

import aiohttp
from fastapi import status, HTTPException, Cookie

from app.schemas import ShowUser
from app.settings import SERVICES_TOKEN
from app.settings import TOKEN_VERIFY_URL
from services_paths import Paths


async def verify_token(token: Annotated[Optional[str], Cookie()] = None) -> Optional[ShowUser]:
    headers = {
        "accept": "application/json",
        "Authorization": f"{token}",
        "Services-Authorization": f"{SERVICES_TOKEN}"
    }
    if not token:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(TOKEN_VERIFY_URL, headers=headers) as response:
            if response.status != status.HTTP_200_OK:
                raise HTTPException(status_code=response.status, detail=await response.json())
            result = await response.json()
            return ShowUser(**result)


def determine_target_url(path: str) -> str:
    split_path = path.split("/")
    if not split_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Путь не найден")

    first_val = split_path[0].replace('-', '_')
    service_info = getattr(Paths, first_val, None)

    if not service_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Путь {first_val} не существует")

    return service_info.value + path
