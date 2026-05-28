import json
import re
import logging
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, AliasChoices
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import LLM
from llama_index.core.tools import FunctionTool

from app.domain.recommendation.entities import ModelProvider, LearningPlan
from app.domain.identity.entities import User
from app.api.v1.schemas.auth import UserPublic
from app.core.config import settings
from app.infrastructure.ai.tavily_search import TavilySearch
from app.infrastructure.ai.model_factory import get_model
from app.infrastructure.ai.prompts.manager import PromptManager

logger = logging.getLogger(__name__)

# Initialize Tavily client
TAVILY_API_KEY = settings.TAVILY_API_KEY
search_client = TavilySearch()


class AgentRecommendation(BaseModel):
    score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        validation_alias=AliasChoices("score", "relevanceScore", "relevance_score"),
        description="Relevance score from 0 to 1",
    )
    reasoning: str = Field(
        default="No reasoning provided.",
        validation_alias=AliasChoices(
            "reasoning", "conclusiveReasoning", "conclusive_reasoning", "reason"
        ),
        description="Brief explanation of why this was recommended",
    )
    tags: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("tags", "descriptionTags", "description_tags", "reason_tags"),
        description="Short tags describing the fit, e.g., 'Matches interests', 'Fills gap'",
    )

    @model_validator(mode="after")
    def validate_cross_fields(self) -> "AgentRecommendation":
        if self.score > 0.8 and len(self.reasoning) < 10:
            raise ValueError("Reasoning must be at least 10 characters long for high scores.")
        return self


async def search_external_resources(query: str) -> str:
    if not TAVILY_API_KEY:
        return "External search is currently unavailable (API key missing)."

    try:
        # Increase results to provide more options
        materials = await search_client.search_educational_materials(query, max_results=5)

        results = []
        for res in materials:
            results.append(f"- [{res['title']}]({res['url']}): {res['description'][:200]}")

        return "\n".join(results) if results else "No external resources found."
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return f"Error searching for external resources: {str(e)}"


def get_advisor_agent(
    llm: LLM,
    transcript_summary: str = "No transcript provided.",
    current_skills: str = "No skills provided.",
    user: Optional[User | UserPublic] = None,
    learning_plan: Optional[LearningPlan] = None,
) -> ReActAgent:
    tools = [FunctionTool.from_defaults(async_fn=search_external_resources)]

    user_context = ""
    if user:
        user_context += f"- User: {user.full_name or user.email}\n"
        if user.career_goal:
            user_context += f"- Career Goal: {user.career_goal}\n"

    plan_context = ""
    if learning_plan:
        plan_context += f"- Current Learning Plan Goal: {learning_plan.goal}\n"
        steps_str = "\n".join(
            [f"  {s.order}. {s.title}: {s.description}" for s in learning_plan.steps]
        )
        plan_context += f"- Plan Steps:\n{steps_str}\n"

    system_prompt = PromptManager.get_advisor_system_prompt(
        user_context=user_context,
        transcript_summary=transcript_summary,
        current_skills=current_skills,
        plan_context=plan_context,
    )

    return ReActAgent(tools=tools, llm=llm, system_prompt=system_prompt)  # type: ignore


def is_capable_model(llm: LLM) -> bool:
    model_name = getattr(llm, "model", getattr(llm, "model_name", ""))
    capable_prefixes = ("gpt-4o", "claude")
    return any(p in model_name.lower() for p in capable_prefixes)


def parse_agent_recommendation(text: str) -> AgentRecommendation:
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            data = json.loads(text)
        return AgentRecommendation(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Could not parse AgentRecommendation from LLM output: {text}") from e
