import uvicorn
from fastapi import FastAPI, APIRouter, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from settings import DEV, SERVICES_TOKEN
from logger.log import config
import aiohttp
from app.state import state
from app.api import (cart_router,
                     cart_item_router,
                     orders_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connector = aiohttp.TCPConnector(limit=300)
    state["http_client"] = aiohttp.ClientSession(connector=connector)
    yield
    await state["http_client"].close()


app = FastAPI(title="shopping_cart", lifespan=lifespan)
main_api_router = APIRouter(prefix="/shopping_cart")

main_api_router.include_router(cart_router)
main_api_router.include_router(cart_item_router)
main_api_router.include_router(orders_router)

app.include_router(main_api_router)

if not DEV:
    @app.middleware("http")
    async def validate_api_token(request: Request, call_next):
        token = request.headers.get("Services-Authorization")
        if token != SERVICES_TOKEN:
            return JSONResponse(status_code=401, content={"message": "Unauthorized microservice"})
        return await call_next(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083, log_config=config)
