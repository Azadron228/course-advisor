from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin_user
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.api.v1.schemas.auth import UserPublic, UserUpdate
from app.core.security import get_password_hash
from app.domain.identity.entities import User
from dataclasses import replace

router = APIRouter()


@router.get("/", response_model=List[UserPublic])
async def read_users(
    db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin_user)
):
    user_repo = UserRepository(db)
    return user_repo.get_all()


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin_user)
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    updated_user = replace(user, **update_data)
    user_repo.update(updated_user)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, db: Session = Depends(get_db), admin_user: User = Depends(get_current_admin_user)
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.delete(user_id)
    return None
