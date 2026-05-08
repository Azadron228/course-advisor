from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    recommendations,
    parser,
    admin,
    users,
    learning_plan,
    chat,
    lessons,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(learning_plan.router, prefix="/learning-plan", tags=["learning-plan"])
