import logging
import re
from typing import List
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.llms import LLM

from app.domain.recommendation.entities import (
    Student,
    SkillGapAnalysis,
    Lesson,
)
from app.domain.catalog.entities import Course

logger = logging.getLogger(__name__)


class GlobalAnalysis(BaseModel):
    title: str
    skill_gap_analysis: SkillGapAnalysis
    learning_path: List[Lesson]


async def generate_global_analysis(llm: LLM, student: Student, courses: List[Course], goal_msg: str, language: str = "en") -> GlobalAnalysis:
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

    parser = PydanticOutputParser(GlobalAnalysis)
    
    prompt_template_str = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        f"OUTPUT LANGUAGE: You MUST provide all text content (titles, descriptions, reasoning) in the following language: {language}.\n\n"
        "1. TITLE: Generate a catchy, professional, and specific title for this learning plan based on the user's goal.\n"
        "2. Skill Gap Map: Identify missing skills and group them by domain.\n"
        "3. Domain Scores: Provide a 0-1 gap score per domain.\n"
        "4. Learning Path: Suggest a logical sequence of internal university courses to achieve the goal.\n"
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
        "STRICT JSON RULES:\n"
        "1. Output ONLY valid JSON matching the schema.\n"
        "2. NO markdown formatting, NO ```json blocks.\n"
        "3. NO trailing commas in lists or objects.\n"
        "4. ALL double quotes within strings MUST be escaped as \\\".\n"
        "5. The output must be exactly ONE JSON object.\n\n"
        "Schema:\n"
        f"{parser.format('')}\n"
    )

    try:
        response = await llm.acomplete(prompt_template_str)
        raw_output = response.text.strip()
        
        # Robust JSON extraction
        # 1. Remove markdown code blocks if present
        raw_output = re.sub(r"^```json\s*", "", raw_output, flags=re.MULTILINE)
        raw_output = re.sub(r"```\s*$", "", raw_output, flags=re.MULTILINE)
        
        # 2. Find the first '{' and last '}'
        start = raw_output.find('{')
        end = raw_output.rfind('}')
        if start != -1 and end != -1:
            raw_output = raw_output[start:end+1]
        
        # 3. Basic cleanup for common LLM JSON mistakes (optional, but safer)
        # Handle trailing commas in objects or arrays
        raw_output = re.sub(r",\s*([}\]])", r"\1", raw_output)
        
        return parser.parse(raw_output)
        
    except Exception as e:
        logger.error(f"Global analysis generation failed: {e}")
        if 'raw_output' in locals():
            logger.error(f"Raw Output: {raw_output}")
        raise

