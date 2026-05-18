from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TranscriptEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    subject_name: str
    credits: float
    mark: float


class Student(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    transcript: List[TranscriptEntry] = Field(default_factory=list)
    current_skills: List[str] = Field(default_factory=list)


class UserPreference(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interest_tags: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_gap: float = 0.0
    content_sim: float = 0.0
    preference: float = 0.0
    rag_reasoning: float = 0.0


class RecommendationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_id: int
    subject_name: str
    score: float
    breakdown: ScoreBreakdown
    reasoning: str
    reason_tags: List[str] = Field(default_factory=list)
    is_external: bool = False
    url: Optional[str] = None


class DomainGap(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    domain: str
    gap_score: float
    missing_skills: List[str] = Field(default_factory=list)


class SkillGapAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    overall_gap_score: float
    domain_breakdown: List[DomainGap] = Field(default_factory=list)
    critical_skills: List[str] = Field(default_factory=list)


class LearningMaterial(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    description: str
    url: Optional[str] = None
    type: str = "article"  # e.g., video, article, course, documentation


class Lesson(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    external_url: Optional[str] = None
    content: Optional[str] = None
    status: str = "upcoming"
    materials: List[LearningMaterial] = Field(default_factory=list)
    score: Optional[int] = None


class UserSkill(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_name: str
    mastery_level: int
    category: str


class LearningPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    goal: str
    steps: List[Lesson] = Field(default_factory=list)
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = Field(default_factory=list)
    language: str = "en"


class SkillNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    label: str
    mastery_level: int
    category: str


class SkillMapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nodes: List[SkillNode] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    results: List[RecommendationResult] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[Lesson] = Field(default_factory=list)


class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    content: str
    created_at: Optional[str] = None


class ChatSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    user_id: int
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessage] = Field(default_factory=list)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    AUTO = "auto"
