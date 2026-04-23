import jwt
import punq
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.domain.identity.entities import User
from app.api.v1.schemas.auth import TokenData
from app.core.config import settings
from app.core.container import get_container
from app.services.advisor_service import AdvisorService
from app.infrastructure.cache.redis_chat import RedisChatHistory

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


# --- DI Helpers ---
def get_service(service_type: type):
    def _get_service(container: punq.Container = Depends(get_container)):
        return container.resolve(service_type)

    return _get_service


def get_advisor_service(service: AdvisorService = Depends(get_service(AdvisorService))):
    return service


def get_chat_history_service(service: RedisChatHistory = Depends(get_service(RedisChatHistory))):
    return service


# --- Existing Deps ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_arq_pool(request: Request):
    return request.app.state.arq_pool


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
