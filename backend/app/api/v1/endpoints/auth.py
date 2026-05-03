from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.schemas.auth import UserCreate, UserPublic, Token
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token, verify_password
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.api.deps import get_db, get_current_active_user
from app.domain.identity.entities import User

router = APIRouter()


def authenticate_user(db: Session, email: str, password: str):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if not user or not user.hashed_password:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/register", response_model=UserPublic)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user_exists = user_repo.get_by_email(user_in.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        id=None, email=user_in.email, full_name=user_in.full_name, hashed_password=hashed_password
    )
    created_user = user_repo.create(new_user)
    return created_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
