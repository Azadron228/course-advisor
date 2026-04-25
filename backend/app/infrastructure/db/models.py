from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, JSON, CheckConstraint, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disabled: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    career_goal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(default=False)


class UserSkillORM(Base):
    __tablename__ = "user_skills"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    mastery_level: Mapped[int] = mapped_column(default=0)  # 0-100
    category: Mapped[str] = mapped_column(String, nullable=False)


class UserTranscriptORM(Base):
    __tablename__ = "user_transcripts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    mark: Mapped[float] = mapped_column(Float, nullable=False)


class LearningPlanORM(Base):
    __tablename__ = "learning_plans"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False)
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class CourseORM(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills_taught: Mapped[dict] = mapped_column(JSON, nullable=False)
    difficulty: Mapped[float] = mapped_column(
        Float, CheckConstraint("difficulty >= 0 AND difficulty <= 1")
    )
    workload: Mapped[float] = mapped_column(
        Float, CheckConstraint("workload >= 0 AND workload <= 1")
    )
    materials_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
