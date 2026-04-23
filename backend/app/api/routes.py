from fastapi import APIRouter
from .v1 import auth, recommendations, parser, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
