from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


@dataclass(frozen=True)
class TranscriptEntry:
    subject_name: str
    credits: float
    mark: float


@dataclass(frozen=True)
class Student:
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]


@dataclass(frozen=True)
class UserPreference:
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float


@dataclass(frozen=True)
class ScoreBreakdown:
    skill_gap: float = 0.0
    content_sim: float = 0.0
    preference: float = 0.0
    rag_reasoning: float = 0.0
    difficulty: float = 0.0
    load: float = 0.0


@dataclass(frozen=True)
class RecommendationResult:
    course_id: str
    subject_name: str
    score: float
    breakdown: ScoreBreakdown
    reasoning: str
    reason_tags: List[str]
    is_external: bool = False
    url: Optional[str] = None


@dataclass(frozen=True)
class DomainGap:
    domain: str
    gap_score: float
    missing_skills: List[str]


@dataclass(frozen=True)
class SkillGapAnalysis:
    overall_gap_score: float
    domain_breakdown: List[DomainGap]
    critical_skills: List[str]


@dataclass(frozen=True)
class LearningMaterial:
    title: str
    description: str
    url: Optional[str] = None
    type: str = "article"  # e.g., video, article, course, documentation


@dataclass(frozen=True)
class LearningPathStep:
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    status: str = "upcoming"
    materials: List[LearningMaterial] = field(default_factory=list)


@dataclass(frozen=True)
class UserSkill:
    skill_name: str
    mastery_level: int
    category: str


@dataclass(frozen=True)
class LearningPlan:
    id: Optional[int]
    goal: str
    steps: List[LearningPathStep]
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SkillNode:
    id: str
    label: str
    mastery_level: int
    category: str


@dataclass(frozen=True)
class SkillMapResponse:
    nodes: List[SkillNode]


@dataclass(frozen=True)
class RecommendationResponse:
    results: List[RecommendationResult]
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[LearningPathStep] = field(default_factory=list)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    AUTO = "auto"
