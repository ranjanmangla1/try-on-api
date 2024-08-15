from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from try_on_api.routes import v1_router
from try_on_api.setup import setup_logger
from loguru import logger
from try_on_api.config import Config


def perform_setup():
    setup_logger(source="server")


def create_app() -> FastAPI:
    perform_setup()

    app = FastAPI()

    origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://sinpie.vercel.app",
    ]

    app.include_router(v1_router(), prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def read_root():
        return {"message": "Hello, World!"}

    logger.info("App created")
    logger.info(f"Config: {Config.API_KEY}")
    return app
