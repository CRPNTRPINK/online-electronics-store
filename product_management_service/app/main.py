import uvicorn
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from settings import DEV, SERVICES_TOKEN
from logger.log import config
from app.api import (attribute_router,
                     category_router,
                     category_attr_router,
                     product_router,
                     image_router,
                     product_attr_router,
                     review_router)

app = FastAPI(title="product_management")
main_api_router = APIRouter(prefix="/product-management")

main_api_router.include_router(category_router)
main_api_router.include_router(attribute_router)
main_api_router.include_router(category_attr_router)
main_api_router.include_router(product_router)
main_api_router.include_router(image_router)
main_api_router.include_router(product_attr_router)
main_api_router.include_router(review_router)

app.include_router(main_api_router)

if not DEV:
    @app.middleware("http")
    async def validate_api_token(request: Request, call_next):
        token = request.headers.get("Services-Authorization")
        if token != SERVICES_TOKEN:
            return JSONResponse(status_code=401, content={"message": "Unauthorized microservice"})
        return await call_next(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082, log_config=config)
