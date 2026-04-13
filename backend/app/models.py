from pydantic import BaseModel, Field
from typing import List, Optional

from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
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

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult] = Field(default_factory=list)
