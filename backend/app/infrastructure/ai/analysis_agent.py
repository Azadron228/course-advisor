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
from app.infrastructure.ai.prompts.manager import PromptManager

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
    prompt_template_str = PromptManager.get_interest_suggestions_prompt(
        goal=goal,
        language=language,
        schema=parser.format(""),
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
    prompt_template_str = PromptManager.get_global_analysis_prompt(
        language=language,
        transcript_summary=transcript_summary,
        current_skills=current_skills,
        goal_msg=goal_msg,
        schema=parser.format(""),
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
