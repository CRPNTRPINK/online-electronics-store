import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from app.settings import SERVICES_TOKEN, DEV
from app.api.handlers import user_router
from app.logger.log import config

app = FastAPI(title="authentication_service")

main_api_router = APIRouter(prefix="/auth")

main_api_router.include_router(user_router)
app.include_router(main_api_router)

if not DEV:
    @app.middleware("http")
    async def validate_api_token(request: Request, call_next):
        token = request.headers.get("Services-Authorization")
        if token != SERVICES_TOKEN:
            return JSONResponse(status_code=401, content={"message": f"Unauthorized microservice"})
        return await call_next(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081, log_config=config)
