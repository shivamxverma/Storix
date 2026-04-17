from fastapi import APIRouter
from app.api.task.router import router as task_router
from app.api.auth.router import router as auth_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(task_router, prefix="/task", tags=["Task"])