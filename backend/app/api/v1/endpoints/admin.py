import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin_user
from app.api.v1.schemas.auth import UserPublic
from app.infrastructure.db.models import UserORM
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users", response_model=List[UserPublic])
async def list_users(db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    users = db.query(UserORM).all()
    return users
