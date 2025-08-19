from fastapi import APIRouter

from app.api.routes import files, operations

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(operations.router, prefix="/operations", tags=["operations"])