from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

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

class LearningPathStep(BaseModel):
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None # Internal course ID or external URL
    is_external: bool = False
    model_config = ConfigDict(from_attributes=True)

class RecommendationResponse(BaseModel):
    results: List[RecommendationResult] = Field(default_factory=list)
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    learning_path: List[LearningPathStep] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
