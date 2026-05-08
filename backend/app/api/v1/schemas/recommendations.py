from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum
from datetime import datetime


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


class RecommendationResult(BaseModel):
    course_id: int
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


class Lesson(BaseModel):
    id: Optional[int] = None
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    status: str = "upcoming"
    materials: List[LearningMaterial] = Field(default_factory=list)
    score: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class LessonSummary(BaseModel):
    id: int
    order: int
    title: str
    description: str
    status: str
    score: Optional[int] = None
    is_external: bool
    model_config = ConfigDict(from_attributes=True)


class LessonDetail(LessonSummary):
    materials: List[LearningMaterial]
    external_url: Optional[str] = None
    content: Optional[str] = None


class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str


class PracticeTestResponse(BaseModel):
    id: int
    lesson_id: int
    questions: List[Question]
    model_config = ConfigDict(from_attributes=True)


class LearningPlan(BaseModel):
    id: Optional[int]
    goal: str
    steps: List[Lesson]
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class LearningPlanSummary(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    step_count: int
    model_config = ConfigDict(from_attributes=True)


class LearningPlanDetail(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    steps: List[LessonSummary]
    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    results: List[RecommendationResult] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[Lesson] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    AUTO = "auto"


class SkillNode(BaseModel):
    id: str
    label: str
    mastery_level: int  # 0 to 100
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
    language: Optional[str] = "en"


class TestSubmissionRequest(BaseModel):
    answers: List[int]


class TestSubmissionResultItem(BaseModel):
    question_index: int
    is_correct: bool
    correct_answer_index: int
    explanation: str


class TestSubmissionResponse(BaseModel):
    score: int
    total: int
    results: List[TestSubmissionResultItem]
