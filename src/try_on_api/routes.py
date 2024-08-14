from importlib import import_module
from fastapi import APIRouter, Depends


def v1_router():
    router = APIRouter(prefix="/v1")
    routes = ("try_cloth_image",)
    for module_name in routes:
        api_module = import_module(f"src.try_on_api.routers.api.v1.{module_name}")
        api_module_router = getattr(api_module, f"{module_name}_router")
        router.include_router(api_module_router)
    return router
