from fastapi import FastAPI, HTTPException

from try_on_api.setup import setup_logger
from loguru import logger

def perform_setup():
    setup_logger(source="server")

def create_app() -> FastAPI:
    perform_setup()

    app = FastAPI()
    #app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_middleware)
    #app.include_router(v1_router(), prefix="/api")
    #app.add_exception_handler(HTTPException, custom_exception_handler)

    @app.get("/")
    async def read_root():
        return {"message": "Hello, World!"}

    logger.info("App created")
    logger.warning("this should work well")
    return app
