from fastapi import Request
from multidict import CIMultiDictProxy
from fastapi.responses import JSONResponse, Response
from typing import Union
from http.cookies import SimpleCookie
from fastapi.datastructures import Headers
from settings import SERVICES_TOKEN

from schemas import ShowUser


def set_service_auth_header(headers: Headers) -> dict:
    headers = dict(headers)
    headers['Services-Authorization'] = SERVICES_TOKEN
    return headers


def set_auth_cookies_request(request: Request, user_info: ShowUser):
    if not user_info:
        return
    del request.cookies["token"]
    request.cookies["user_id"] = str(user_info.user_id)


def set_headers_response(headers: CIMultiDictProxy[str], response: Union[JSONResponse, Response]):
    for key, value in headers.items():
        response.headers[key] = value
