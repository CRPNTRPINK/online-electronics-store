import uvicorn
from fastapi import FastAPI
from handlers import gateway_router
from logger.log import config

app = FastAPI(title="api/v1")
app.include_router(gateway_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=config)
