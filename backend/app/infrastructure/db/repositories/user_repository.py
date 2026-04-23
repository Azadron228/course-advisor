from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.models import UserORM
from app.domain.identity.entities import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        o = self.db.scalar(select(UserORM).where(UserORM.email == email))
        if not o:
            return None
        return User(
            id=o.id,
            email=o.email,
            full_name=o.full_name,
            disabled=o.disabled,
            is_admin=o.is_admin,
            hashed_password=o.hashed_password
        )

    def create(self, user: User) -> User:
        db_user = UserORM(
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_admin=user.is_admin,
            disabled=user.disabled
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        user.id = db_user.id
        return user
