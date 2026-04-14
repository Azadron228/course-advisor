from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, JSON, CheckConstraint, Text
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from enum import Enum

class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disabled: Mapped[bool] = mapped_column(default=False)

class CourseORM(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills_taught: Mapped[dict] = mapped_column(JSON, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, CheckConstraint('difficulty >= 0 AND difficulty <= 1'))
    workload: Mapped[float] = mapped_column(Float, CheckConstraint('workload >= 0 AND workload <= 1'))
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(User):
    id: int

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AUTO = "auto"

class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float = Field(ge=0, le=100)

class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]

class Course(BaseModel):
    id: str
    subject_name: str
    credits: float
    description: str
    prerequisites: List[str]
    skills_taught: List[str]
    difficulty: float = Field(ge=0, le=1)
    workload: float = Field(ge=0, le=1)

class UserPreference(BaseModel):
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float

class ScoreBreakdown(BaseModel):
    skill_gap: float = 0.0
    content_sim: float = 0.0
    preference: float = 0.0
    rag_reasoning: float = 0.0
    difficulty: float = 0.0
    load: float = 0.0

class RecommendationResult(BaseModel):
    course_id: str
    subject_name: str
    score: float = 0.0
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    reasoning: str = "No reasoning available."
    reason_tags: List[str] = Field(default_factory=list)
    is_external: bool = False
    url: Optional[str] = None

class DomainGap(BaseModel):
    domain: str
    gap_score: float = Field(ge=0, le=1)
    missing_skills: List[str]

class SkillGapAnalysis(BaseModel):
    overall_gap_score: float
    domain_breakdown: List[DomainGap]
    critical_skills: List[str]

class LearningPathStep(BaseModel):
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None # Internal course ID or external URL
    is_external: bool = False

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[LearningPathStep] = Field(default_factory=list)
