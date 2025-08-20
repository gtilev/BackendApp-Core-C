from fastapi import APIRouter

from app.api.routes import files, operations, auth, system

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])
api_router.include_router(system.router, prefix="/system", tags=["system"])