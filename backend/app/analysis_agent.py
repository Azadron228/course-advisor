import os
import json
import re
import logging
from dataclasses import dataclass
from typing import Any, List, Optional
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from .schemas.course import Student, CoursePublic as Course
from .schemas.recommendation import SkillGapAnalysis, LearningPathStep
from .schemas.internal import ModelProvider
from .agent import get_model, is_capable_model

logger = logging.getLogger(__name__)

class GlobalAnalysis(BaseModel):
    skill_gap_analysis: SkillGapAnalysis
    learning_path: List[LearningPathStep]

@dataclass
class AnalysisDeps:
    student: Student
    courses: List[Course]

analysis_agent = Agent(
    model=get_model(),
    output_type=GlobalAnalysis,
    deps_type=AnalysisDeps,
    retries=3,
    system_prompt=(
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        "1. Skill Gap Map: Identify missing skills and group them by domain (e.g., Programming, AI, Cybersecurity).\n"
        "2. Domain Scores: Provide a 0-1 gap score per domain (1 = huge gap, 0 = fully covered).\n"
        "3. Learning Path: Suggest a logical sequence of courses (internal or external) to fill these gaps.\n"
        "Always prioritize filling critical prerequisites and foundational skills first."
    )
)

@analysis_agent.system_prompt
def get_analysis_prompt(ctx: RunContext[AnalysisDeps]) -> str:
    student = ctx.deps.student
    courses = ctx.deps.courses
    
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    available_courses = "\n".join([f"- {c.subject_name} (ID: {c.id}): {c.description}" for c in courses])
    
    return (
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"Available Internal Courses:\n{available_courses}\n\n"
        "Generate a SkillGapAnalysis and a LearningPath. Be precise and strategic."
    )

def parse_global_analysis(text: str) -> GlobalAnalysis:
    try:
        data = json.loads(text)
        return GlobalAnalysis(**data)
    except Exception as e:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             try:
                 return GlobalAnalysis(**json.loads(match.group()))
             except Exception:
                 pass
        raise ValueError(f"Could not parse GlobalAnalysis: {text}") from e
