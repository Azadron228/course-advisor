from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    disabled: Mapped[bool] = mapped_column(default=False)
    onboarding_completed: Mapped[bool] = mapped_column(default=False)
    career_goal: Mapped[str] = mapped_column(Text, nullable=True)
    interests: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Preferences
    default_skill_level: Mapped[str] = mapped_column(String, nullable=False, default="Beginner")
    default_learning_style: Mapped[str] = mapped_column(String, nullable=False, default="Practical")
    default_study_time: Mapped[int] = mapped_column(default=10)


class UserSkillORM(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String, nullable=True)


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
    is_active: Mapped[bool] = mapped_column(default=True)
    skill_level: Mapped[str] = mapped_column(String, nullable=False, default="Beginner")
    learning_style: Mapped[str] = mapped_column(String, nullable=False, default="Practical")
    study_time: Mapped[int] = mapped_column(default=10)
    interests: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    last_interacted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # New relationship
    lessons: Mapped[List["LessonORM"]] = relationship(
        "LessonORM", back_populates="plan", cascade="all, delete-orphan", order_by="LessonORM.order"
    )


class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="upcoming")
    is_external: Mapped[bool] = mapped_column(default=False)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_resources: Mapped[List[dict]] = mapped_column(JSON, nullable=False, default=list)

    plan: Mapped["LearningPlanORM"] = relationship("LearningPlanORM", back_populates="lessons")


class ChatSessionORM(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)  # ISO format
    updated_at: Mapped[str] = mapped_column(String, nullable=False)  # ISO format


class ChatMessageORM(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)  # ISO format


class PracticeTestORM(Base):
    __tablename__ = "practice_tests"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=False)  # questions, options, answers
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class UserTestScoreORM(Base):
    __tablename__ = "user_test_scores"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    answers: Mapped[dict] = mapped_column(JSON, nullable=True)  # Store user's submitted answers
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
