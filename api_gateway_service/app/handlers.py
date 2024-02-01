from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from dependecies import determine_target_url, verify_token
import aiohttp
from schemas import ShowUser
from typing import Annotated, Optional
from utils import set_auth_cookies_request, set_headers_response, set_service_auth_header

gateway_router = APIRouter(prefix='/api/v1', tags=['api-gateway'])


@gateway_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(request: Request,
                        target_url: Annotated[str, Depends(determine_target_url)],
                        user_info: Annotated[Optional[ShowUser], Depends(verify_token)]):
    try:
        set_auth_cookies_request(request, user_info)
        headers = set_service_auth_header(request.headers)
        async with aiohttp.ClientSession() as session:
            async with session.request(request.method,
                                       target_url,
                                       data=await request.body(),
                                       headers=headers) as response:
                if response.status in (200, 201):
                    json_response = JSONResponse(status_code=response.status, content=await response.json())
                    set_headers_response(response.headers, json_response)
                    return json_response
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(er.args[-1]))
