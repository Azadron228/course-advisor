from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum


class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float


class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]


class UserPreference(BaseModel):
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: Optional[str] = None


class ChatSession(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class ChatSessionDetail(ChatSession):
    messages: List[ChatMessage] = []


class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]
    session_id: int


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
    model_config = ConfigDict(from_attributes=True)


class DomainGap(BaseModel):
    domain: str
    gap_score: float = Field(ge=0, le=1)
    missing_skills: List[str]


class SkillGapAnalysis(BaseModel):
    overall_gap_score: float
    domain_breakdown: List[DomainGap]
    critical_skills: List[str]
    model_config = ConfigDict(from_attributes=True)


class LearningMaterial(BaseModel):
    title: str
    description: str
    url: Optional[str] = None
    type: str = "article"
    model_config = ConfigDict(from_attributes=True)


class LearningPathStep(BaseModel):
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    status: str = "upcoming"
    materials: List[LearningMaterial] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class LearningPlan(BaseModel):
    id: Optional[int]
    goal: str
    steps: List[LearningPathStep]
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    results: List[RecommendationResult] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[LearningPathStep] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    AUTO = "auto"

class SkillNode(BaseModel):
    id: str
    label: str
    mastery_level: int # 0 to 100
    category: str

class SkillMapResponse(BaseModel):
    nodes: List[SkillNode]


class PlanGenerateRequest(BaseModel):
    goal: str
    skill_level: str
    learning_style: str
    study_time: int
    interests: List[str]
    transcript: Optional[List[TranscriptEntry]] = None
