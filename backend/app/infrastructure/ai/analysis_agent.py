import logging
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


async def generate_global_analysis(llm: LLM, student: Student, courses: List[Course], goal_msg: str) -> GlobalAnalysis:
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    
    available_courses = ""
    for c in courses:
        available_courses += f"- {c.subject_name} (Course ID: {c.id}): {c.description}\n"
        if c.materials:
            available_courses += "  Available Lessons:\n"
            for m in c.materials:
                available_courses += f"    * {m.filename} (Lesson ID: {m.id})\n"
    available_courses = available_courses.strip()

    prompt_template_str = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        "1. Skill Gap Map: Identify missing skills and group them by domain.\n"
        "2. Domain Scores: Provide a 0-1 gap score per domain.\n"
        "3. Learning Path: Suggest a logical sequence of internal university courses to achieve the goal.\n"
        "   - INTERNAL FIRST: If an internal course (from the list below) covers a needed skill, you MUST use it.\n"
        "   - RESOURCE ID: For internal steps, you MUST provide the specific Lesson ID (e.g., '1', '5') as 'resource_id'. Pick the most relevant lesson from the course.\n"
        "   - NO EXTERNAL COURSES: Do NOT recommend courses from Coursera, Udemy, edX, or other platforms.\n"
        "   - SUPPLEMENTARY MATERIALS: EVERY step involving an internal course MUST include 1-2 high-quality "
        "     external materials (official documentation, YouTube videos, or technical articles) as extra help.\n"
        "   - GAP FILLING: If no internal course covers a mandatory prerequisite (e.g., Python), create a step "
        "     using ONLY external materials (documentation/tutorials) as the resource. Mark these as external steps.\n"
        "   - EVERY step MUST include at least 1-2 detailed materials.\n"
        "   - Materials MUST have a 'title', a 'description' (2-3 sentences explaining what to learn), and a 'url' if external.\n\n"
        "Always prioritize filling critical prerequisites and foundational skills first.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"Available Internal Courses:\n{available_courses}\n\n"
        f"User Goal and Context: {goal_msg}\n\n"
        "Output ONLY valid JSON matching the schema. Example format:\n"
        "{\n"
        '  "skill_gap_analysis": {\n'
        '    "overall_gap_score": 0.5,\n'
        '    "domain_breakdown": [\n'
        '      {"domain": "Programming", "gap_score": 0.3, "missing_skills": ["Python", "Algorithms"]}\n'
        '    ],\n'
        '    "critical_skills": ["Python"]\n'
        '  },\n'
        '  "learning_path": [\n'
        '    {\n'
        '      "order": 1,\n'
        '      "title": "Introduction to Computer Science",\n'
        '      "description": "Learn the basics of computer science using internal course 101.",\n'
        '      "resource_id": "101",\n'
        '      "is_external": false,\n'
        '      "status": "current",\n'
        '      "materials": [\n'
        '        {"title": "Python Basics", "description": "Official documentation for Python.", "url": "https://python.org", "type": "documentation"}\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=GlobalAnalysis,
        llm=llm,
        prompt_template_str=prompt_template_str,
        verbose=True,
    )

    try:
        return await program.acall()
    except Exception as e:
        logger.error(f"Global analysis generation failed: {e}")
        # Log more info if possible
        raise
