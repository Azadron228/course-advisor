import os
import json
import re
import logging
from dataclasses import dataclass
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import LLM

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

def get_analysis_agent(llm: LLM, student: Student, courses: List[Course]) -> ReActAgent:
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    available_courses = "\n".join([f"- {c.subject_name} (ID: {c.id}): {c.description}" for c in courses])
    
    system_prompt = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        "1. Skill Gap Map: Identify missing skills and group them by domain (e.g., Programming, AI, Cybersecurity).\n"
        "2. Domain Scores: Provide a 0-1 gap score per domain (1 = huge gap, 0 = fully covered).\n"
        "3. Learning Path: Suggest a logical sequence of courses (internal or external) to fill these gaps.\n"
        "Always prioritize filling critical prerequisites and foundational skills first.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"Available Internal Courses:\n{available_courses}\n\n"
        "Output MUST be ONLY a valid JSON object matching the GlobalAnalysis schema with fields: skill_gap_analysis, learning_path."
    )
    
    return ReActAgent(
        tools=[], # No tools for this agent currently
        llm=llm,
        verbose=True,
        system_prompt=system_prompt
    )

def parse_global_analysis(text: str) -> GlobalAnalysis:
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             data = json.loads(match.group())
        else:
             data = json.loads(text)
        return GlobalAnalysis(**data)
    except Exception as e:
        raise ValueError(f"Could not parse GlobalAnalysis: {text}") from e
