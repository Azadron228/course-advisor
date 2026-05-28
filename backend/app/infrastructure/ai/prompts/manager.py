import os
from pathlib import Path
from llama_index.core import PromptTemplate


class PromptManager:
    """Manages loading and formatting of LLM prompt templates from files."""

    _PROMPTS_DIR = Path(__file__).parent.resolve()

    @classmethod
    def load_prompt(cls, filename: str) -> str:
        """Loads a raw prompt template from the prompts directory."""
        file_path = cls._PROMPTS_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_advisor_system_prompt(
        cls,
        user_context: str,
        transcript_summary: str,
        current_skills: str,
        plan_context: str,
    ) -> str:
        """Loads and formats the advisor system prompt."""
        template_str = cls.load_prompt("advisor_system.txt")
        template = PromptTemplate(template_str)
        return template.format(
            user_context=user_context,
            transcript_summary=transcript_summary,
            current_skills=current_skills,
            plan_context=plan_context,
        )

    @classmethod
    def get_interest_suggestions_prompt(
        cls,
        goal: str,
        language: str,
        schema: str,
    ) -> str:
        """Loads and formats the interest suggestions prompt."""
        template_str = cls.load_prompt("interest_suggestions.txt")
        template = PromptTemplate(template_str)
        return template.format(
            goal=goal,
            language=language,
            schema=schema,
        )

    @classmethod
    def get_global_analysis_prompt(
        cls,
        language: str,
        transcript_summary: str,
        current_skills: str,
        goal_msg: str,
        schema: str,
    ) -> str:
        """Loads and formats the global analysis prompt."""
        template_str = cls.load_prompt("global_analysis.txt")
        template = PromptTemplate(template_str)
        return template.format(
            language=language,
            transcript_summary=transcript_summary,
            current_skills=current_skills,
            goal_msg=goal_msg,
            schema=schema,
        )
