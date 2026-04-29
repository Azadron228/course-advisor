import json
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, AliasChoices
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.tools import FunctionTool

from app.domain.recommendation.entities import ModelProvider, Student, LearningPlan
from app.domain.catalog.entities import Course
from app.domain.identity.entities import User
from app.core.config import settings
from tavily import TavilyClient

logger = logging.getLogger(__name__)

# Initialize Tavily client
TAVILY_API_KEY = settings.TAVILY_API_KEY


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
        description="Brief explanation of why this course was recommended",
    )
    tags: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("tags", "descriptionTags", "description_tags", "reason_tags"),
        description="Short tags describing the fit, e.g., 'Matches interests', 'Fills gap'",
    )

    @model_validator(mode="after")
    def validate_cross_fields(self) -> "AgentRecommendation":
        # Requirement 4: cross-field business logic
        if self.score > 0.8 and len(self.reasoning) < 10:
            raise ValueError("Reasoning must be at least 10 characters long for high scores.")
        return self


@dataclass
class AgentDeps:
    student: Student
    course: Course


def get_model(provider: ModelProvider = ModelProvider.AUTO) -> LLM:
    # Auto-detection logic - default to OpenAI
    if provider == ModelProvider.AUTO:
        provider = ModelProvider.OPENAI

    if provider == ModelProvider.OPENAI:
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == "sk-placeholder-key" or api_key == "sk-dummy":
            raise ValueError("OPENAI_API_KEY is missing or invalid. Please provide a valid OpenAI API key.")
        return OpenAI(model="gpt-5.4-nano", api_key=api_key)

    raise ValueError(f"Unsupported model provider: {provider}")


async def search_external_resources(query: str) -> str:
    """
    Search for high-quality external online courses or learning resources (Coursera, edX, YouTube, Documentation)
    to supplement the student's learning path or fill specific skill gaps not covered by the internal course.
    """
    if not TAVILY_API_KEY:
        return "External search is currently unavailable (API key missing)."

    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        # Search for online courses specifically
        search_query = f"best online courses or tutorials for {query} on Coursera edX Udemy"
        response = tavily.search(query=search_query, search_depth="basic", max_results=3)

        results = []
        for res in response.get("results", []):
            results.append(f"- [{res['title']}]({res['url']}): {res['content'][:200]}...")

        return "\n".join(results) if results else "No external resources found."
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return f"Error searching for external resources: {str(e)}"


def get_recommendation_agent(llm: LLM, student: Student, course: Course) -> ReActAgent:
    tools = [FunctionTool.from_defaults(async_fn=search_external_resources)]

    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    course_skills = ", ".join(course.skills_taught)
    materials_prompt = (
        f"\nAdditional Course Materials (Text extracted from syllabi/notes): {course.materials_content}"
        if course.materials_content
        else ""
    )

    system_prompt = (
        f"You are a professional university advisor. "
        f"Your task is to analyze a student's transcript and current skills "
        f"against a specific course description, its taught skills, and supplementary materials. "
        f"Provide a relevance score (0-1) in a field named 'score', "
        f"a concise reasoning in a field named 'reasoning', "
        f"and descriptive tags in a field named 'tags'.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n"
        f"Internal Course: {course.subject_name}\n"
        f"Internal Course Description: {course.description}\n"
        f"Skills Taught in Internal Course: {course_skills}\n"
        f"{materials_prompt}\n\n"
        f"If the internal course has significant skill gaps or if the student needs supplementary "
        f"learning, you MUST use the 'search_external_resources' tool to find 1-2 high-quality "
        f"online courses (Coursera, edX, Udemy) or documentation. "
        f"Include these in your reasoning if relevant.\n\n"
        f"Output MUST be ONLY a valid JSON object with the fields: score, reasoning, tags."
    )

    return ReActAgent(tools=tools, llm=llm, verbose=False, system_prompt=system_prompt)


def get_advisor_agent(
    llm: LLM,
    transcript_summary: str = "No transcript provided.",
    current_skills: str = "No skills provided.",
    user: Optional[User] = None,
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

    system_prompt = (
        "You are a professional university academic advisor. "
        "Your goal is to help students with course selection, career advice, and learning strategies. "
        "Use your knowledge and available tools to provide high-quality, personalized guidance.\n\n"
        "Student Academic Context:\n"
        f"{user_context}"
        f"- Completed/Current Courses: {transcript_summary}\n"
        f"- Current Skills: {current_skills}\n"
        f"{plan_context}\n"
        "When giving advice, consider the student's background and goals. If you need to suggest external resources, "
        "use the 'search_external_resources' tool. Be professional, supportive, and concise.\n\n"
        "IMPORTANT: You MUST always conclude your response with 'Final Answer: ' followed by your advice. "
        "Do not include your internal thoughts or tool calls in the final response to the student."
    )

    return ReActAgent(tools=tools, llm=llm, verbose=False, system_prompt=system_prompt)


def is_capable_model(llm: LLM) -> bool:
    model_name = getattr(llm, "model", getattr(llm, "model_name", ""))
    capable_prefixes = ("gpt-5.4", "claude")
    return any(p in model_name.lower() for p in capable_prefixes)


def parse_agent_recommendation(text: str) -> AgentRecommendation:
    try:
        # LlamaIndex agents sometimes wrap JSON in code blocks
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            data = json.loads(text)
        return AgentRecommendation(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Could not parse AgentRecommendation from LLM output: {text}") from e
