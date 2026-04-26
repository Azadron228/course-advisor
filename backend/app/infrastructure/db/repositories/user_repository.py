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
            hashed_password=o.hashed_password,
            career_goal=o.career_goal,
            onboarding_completed=o.onboarding_completed,
            interests=o.interests,
            default_skill_level=o.default_skill_level,
            default_learning_style=o.default_learning_style,
            default_study_time=o.default_study_time,
        )

    def create(self, user: User) -> User:
        db_user = UserORM(
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_admin=user.is_admin,
            disabled=user.disabled,
            career_goal=user.career_goal,
            onboarding_completed=user.onboarding_completed,
            interests=user.interests,
            default_skill_level=user.default_skill_level,
            default_learning_style=user.default_learning_style,
            default_study_time=user.default_study_time,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        user.id = db_user.id
        return user

    def get_all(self) -> list[User]:
        orms = self.db.scalars(select(UserORM)).all()
        return [
            User(
                id=o.id,
                email=o.email,
                full_name=o.full_name,
                disabled=o.disabled,
                is_admin=o.is_admin,
                hashed_password=o.hashed_password,
                career_goal=o.career_goal,
                onboarding_completed=o.onboarding_completed,
            )
            for o in orms
        ]

    def get_by_id(self, user_id: int) -> User | None:
        o = self.db.scalar(select(UserORM).where(UserORM.id == user_id))
        if not o:
            return None
        return User(
            id=o.id,
            email=o.email,
            full_name=o.full_name,
            disabled=o.disabled,
            is_admin=o.is_admin,
            hashed_password=o.hashed_password,
            career_goal=o.career_goal,
            onboarding_completed=o.onboarding_completed,
            interests=o.interests,
            default_skill_level=o.default_skill_level,
            default_learning_style=o.default_learning_style,
            default_study_time=o.default_study_time,
        )

    def update(self, user: User) -> User:
        o = self.db.scalar(select(UserORM).where(UserORM.id == user.id))
        if not o:
            raise Exception("User not found")

        o.email = user.email
        o.full_name = user.full_name
        o.is_admin = user.is_admin
        o.disabled = user.disabled
        o.career_goal = user.career_goal
        o.onboarding_completed = user.onboarding_completed
        o.interests = user.interests
        o.default_skill_level = user.default_skill_level
        o.default_learning_style = user.default_learning_style
        o.default_study_time = user.default_study_time
        if user.hashed_password:
            o.hashed_password = user.hashed_password

        self.db.commit()
        self.db.refresh(o)
        return user

    def delete(self, user_id: int) -> None:
        o = self.db.scalar(select(UserORM).where(UserORM.id == user_id))
        if o:
            self.db.delete(o)
            self.db.commit()
