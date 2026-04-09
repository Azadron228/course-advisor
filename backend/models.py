from pydantic import BaseModel, Field
from typing import List, Optional

from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"

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
    skill_gap: float
    content_sim: float
    preference: float
    rag_reasoning: float
    difficulty: float
    load: float

class RecommendationResult(BaseModel):
    course_id: str
    subject_name: str
    score: float
    breakdown: ScoreBreakdown
    reasoning: str
    reason_tags: List[str]
    is_external: bool = False
    url: Optional[str] = None

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult]
