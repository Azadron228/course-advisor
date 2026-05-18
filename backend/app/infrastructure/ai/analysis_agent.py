import logging
import re
from typing import List, Any
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.llms import LLM

from app.domain.recommendation.entities import (
    Student,
    SkillGapAnalysis,
    Lesson,
    LearningMaterial,
)

logger = logging.getLogger(__name__)


class LessonPlanStep(BaseModel):
    order: int
    title: str
    description: str
    is_external: bool = True


class GlobalAnalysis(BaseModel):
    title: str
    skill_gap_analysis: SkillGapAnalysis
    learning_path: List[LessonPlanStep]


class InterestSuggestions(BaseModel):
    interests: List[str]


async def suggest_interests(llm: LLM, goal: str, language: str = "en") -> List[str]:
    parser = PydanticOutputParser(InterestSuggestions)

    prompt_template_str = (
        "You are an expert career advisor. Your goal is to suggest 5-8 relevant, specific, and professional interest tags "
        "or specific topics that a student should focus on to achieve their career goal.\n\n"
        f"USER CAREER GOAL: {goal}\n\n"
        f"OUTPUT LANGUAGE: You MUST provide all tags in the following language: {language}.\n\n"
        "1. TAGS: Generate 5-8 tags. Each tag should be 1-3 words long.\n"
        "2. SPECIFICITY: Avoid generic tags like 'Programming' if the goal is 'React Developer'. Use 'State Management', 'Component Architecture', etc.\n\n"
        "STRICT JSON RULES:\n"
        "1. Output ONLY valid JSON matching the schema.\n"
        "2. NO markdown formatting, NO ```json blocks.\n"
        "Schema:\n"
        f"{parser.format('')}\n"
    )

    try:
        response = await llm.acomplete(prompt_template_str)
        raw_output = response.text.strip()

        # Robust JSON extraction
        raw_output = re.sub(r"^```json\s*", "", raw_output, flags=re.MULTILINE)
        raw_output = re.sub(r"```\s*$", "", raw_output, flags=re.MULTILINE)

        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1:
            raw_output = raw_output[start : end + 1]

        raw_output = "".join(c for c in raw_output if ord(c) >= 32 or c in "\n\r\t")

        try:
            parsed = parser.parse(raw_output)
            return parsed.interests
        except Exception:
            clean_output = re.sub(r",\s*\}", "}", raw_output)
            clean_output = re.sub(r",\s*\]", "]", clean_output)
            parsed = parser.parse(clean_output)
            return parsed.interests

    except Exception as e:
        logger.error(f"Interest suggestion failed: {e}")
        return []


async def generate_global_analysis(
    llm: LLM, student: Student, courses: List[Any], goal_msg: str, language: str = "en"
) -> GlobalAnalysis:
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)

    parser = PydanticOutputParser(GlobalAnalysis)

    prompt_template_str = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript.\n\n"
        f"OUTPUT LANGUAGE: You MUST provide all text content (titles, descriptions, reasoning) in the following language: {language}.\n\n"
        "1. TITLE: Generate a VERY SHORT (2-5 words), catchy, professional, and specific title for this learning plan based on the user's goal.\n"
        "2. Skill Gap Map: Identify missing skills and group them by domain.\n"
        "3. Domain Scores: Provide a 0-1 gap score per domain.\n"
        "4. Learning Path: Suggest a logical sequence of learning steps to achieve the goal.\n"
        "   - LESSON TITLES: Each lesson title MUST be VERY SHORT and concise (2-4 words).\n"
        "   - ALL STEPS ARE EXTERNAL/AI-GENERATED: You must generate the steps yourself. Do not rely on internal university courses.\n"
        "   - Set `is_external` to true for all steps.\n\n"
        "Always prioritize filling critical prerequisites and foundational skills first.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"User Goal and Context: {goal_msg}\n\n"
        "STRICT JSON RULES:\n"
        "1. Output ONLY valid JSON matching the schema.\n"
        "2. NO markdown formatting, NO ```json blocks.\n"
        "3. NO trailing commas in lists or objects.\n"
        '4. ALL double quotes within strings MUST be escaped as \\".\n'
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
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1:
            raw_output = raw_output[start : end + 1]

        # 3. Final cleanup - remove any non-printable characters that might break the parser
        # but keep newlines and common whitespace
        raw_output = "".join(c for c in raw_output if ord(c) >= 32 or c in "\n\r\t")

        try:
            return parser.parse(raw_output)
        except Exception:
            # If standard parser fails, try one more cleanup for common trailing commas
            # but only at the very end of objects/arrays (less aggressive)
            clean_output = re.sub(r",\s*\}", "}", raw_output)
            clean_output = re.sub(r",\s*\]", "]", clean_output)
            return parser.parse(clean_output)

    except Exception as e:
        logger.error(f"Global analysis generation failed: {e}")
        if "raw_output" in locals():
            logger.error(f"Raw Output Length: {len(raw_output)}")
            logger.error(f"Raw Output (first 500): {raw_output[:500]}")
            logger.error(f"Raw Output (last 500): {raw_output[-500:]}")
            # Write to a predictable temp file for the agent to read
            try:
                with open("/tmp/last_failed_json.json", "w") as f:
                    f.write(raw_output)
                logger.info("Saved failed JSON to /tmp/last_failed_json.json")
            except Exception:
                pass
        raise
