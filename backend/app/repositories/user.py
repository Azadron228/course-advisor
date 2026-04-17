from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import UserORM
import json

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> UserORM | None:
        return self.db.scalar(select(UserORM).where(UserORM.email == email))

    def create(self, email: str, hashed_password: str, full_name: str | None = None, is_admin: bool = False) -> UserORM:
        db_user = UserORM(email=email, hashed_password=hashed_password, full_name=full_name, is_admin=is_admin)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
