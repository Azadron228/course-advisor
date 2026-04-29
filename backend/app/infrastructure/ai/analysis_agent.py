import json
import re
import logging
from dataclasses import dataclass
from typing import List
from pydantic import BaseModel
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.llms import LLM

from app.domain.recommendation.entities import (
    Student,
    SkillGapAnalysis,
    LearningPathStep,
)
from app.domain.catalog.entities import Course

logger = logging.getLogger(__name__)


class GlobalAnalysis(BaseModel):
    skill_gap_analysis: SkillGapAnalysis
    learning_path: List[LearningPathStep]


@dataclass
class AnalysisDeps:
    student: Student
    courses: List[Course]


async def generate_global_analysis(llm: LLM, student: Student, courses: List[Course], goal_msg: str) -> GlobalAnalysis:
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    available_courses = "\n".join(
        [f"- {c.subject_name} (ID: {c.id}): {c.description}" for c in courses]
    )

    prompt_template_str = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        "1. Skill Gap Map: Identify missing skills and group them by domain.\n"
        "2. Domain Scores: Provide a 0-1 gap score per domain.\n"
        "3. Learning Path: Suggest a logical sequence of courses (internal or external) to fill these gaps.\n"
        "   - EVERY step MUST include at least 1-2 detailed materials.\n"
        "   - Materials MUST have a 'title', a 'description' (at least 2-3 sentences of detailed content/what to learn), and a 'url' if external.\n"
        "   - If the step uses an internal course, include it as a material with its details.\n"
        "   - If external, provide high-quality links (Coursera, edX, YouTube, Documentation).\n\n"
        "Always prioritize filling critical prerequisites and foundational skills first.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"Available Internal Courses:\n{available_courses}\n\n"
        f"User Goal and Context: {goal_msg}\n\n"
        "Output ONLY valid JSON matching the schema."
    )

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=GlobalAnalysis,
        llm=llm,
        prompt_template_str=prompt_template_str,
        verbose=True,
    )

    return await program.acall()


def parse_global_analysis(text: str) -> GlobalAnalysis:
    # This is kept for backward compatibility if needed, but we should prefer generate_global_analysis
    try:
        # LlamaIndex sometimes prefixes with 'assistant: ' or wraps in markdown
        json_text = text
        if text.startswith("assistant: "):
            json_text = text[len("assistant: "):]
        
        match = re.search(r"\{.*\}", json_text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            data = json.loads(json_text)
        return GlobalAnalysis(**data)
    except Exception as e:
        logger.error(f"Failed to parse GlobalAnalysis. Error: {e}. Text: {text}")
        raise ValueError(f"Could not parse GlobalAnalysis: {text}") from e
