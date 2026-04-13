import os
import json
import re
import logging
from dataclasses import dataclass
from typing import Any, Union, Type, List, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic import BaseModel, Field, model_validator, AliasChoices
from .models import ModelProvider, Student, Course
from tavily import TavilyClient

logger = logging.getLogger(__name__)

# Initialize Tavily client
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class AgentRecommendation(BaseModel):
    score: float = Field(
        default=0.0,
        ge=0, le=1, 
        validation_alias=AliasChoices('score', 'relevanceScore', 'relevance_score'),
        description="Relevance score from 0 to 1"
    )
    reasoning: str = Field(
        default="No reasoning provided.",
        validation_alias=AliasChoices('reasoning', 'conclusiveReasoning', 'conclusive_reasoning', 'reason'),
        description="Brief explanation of why this course was recommended"
    )
    tags: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices('tags', 'descriptionTags', 'description_tags', 'reason_tags'),
        description="Short tags describing the fit, e.g., 'Matches interests', 'Fills gap'"
    )

    @model_validator(mode='after')
    def validate_cross_fields(self) -> 'AgentRecommendation':
        # Requirement 4: cross-field business logic
        if self.score > 0.8 and len(self.reasoning) < 10:
             raise ValueError("Reasoning must be at least 10 characters long for high scores.")
        return self

@dataclass
class AgentDeps:
    student: Student
    course: Course

def get_model(provider: ModelProvider = ModelProvider.AUTO):
    # Auto-detection logic
    if provider == ModelProvider.AUTO:
        if os.getenv("GOOGLE_API_KEY"):
            provider = ModelProvider.GEMINI
        elif os.getenv("OPENAI_API_KEY"):
            provider = ModelProvider.OPENAI
        elif os.getenv("OLLAMA_BASE_URL"):
            provider = ModelProvider.OLLAMA
        else:
            return TestModel()
    
    if provider == ModelProvider.GEMINI:
        return GoogleModel(
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
        )

    if provider == ModelProvider.OLLAMA:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        provider_obj = OpenAIProvider(
            base_url=f"{base_url}/v1",
            api_key='ollama',
        )
        return OpenAIChatModel(
            model_name='llama3.2', # Standardized to llama3.2
            provider=provider_obj,
        )
    
    if provider == ModelProvider.OPENAI:
        if not os.getenv("OPENAI_API_KEY"):
            return TestModel()
        return OpenAIChatModel('gpt-4o')

    return TestModel()

recommendation_agent = Agent(
    model=get_model(),
    output_type=AgentRecommendation,
    deps_type=AgentDeps,
    retries=3,
)

@recommendation_agent.system_prompt
def get_system_prompt(ctx: RunContext[AgentDeps]) -> str:
    # Requirement 2: remove globals from prompt, use deps
    student = ctx.deps.student
    course = ctx.deps.course
    transcript_summary = ", ".join([e.subject_name for e in student.transcript])
    current_skills = ", ".join(student.current_skills)
    course_skills = ", ".join(course.skills_taught)
    
    return (
        f"You are a professional university advisor. "
        f"Your task is to analyze a student's transcript and current skills "
        f"against a specific course description and its taught skills. "
        f"Provide a relevance score (0-1) in a field named 'score', "
        f"a concise reasoning in a field named 'reasoning', "
        f"and descriptive tags in a field named 'tags'.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n"
        f"Internal Course: {course.subject_name}\n"
        f"Internal Course Description: {course.description}\n"
        f"Skills Taught in Internal Course: {course_skills}\n\n"
        f"If the internal course has significant skill gaps or if the student needs supplementary "
        f"learning, you MUST use the 'search_external_resources' tool to find 1-2 high-quality "
        f"online courses (Coursera, edX, Udemy) or documentation. "
        f"Include these in your reasoning if relevant."
    )

@recommendation_agent.tool
async def search_external_resources(ctx: RunContext[AgentDeps], query: str) -> str:
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
        for res in response.get('results', []):
            results.append(f"- [{res['title']}]({res['url']}): {res['content'][:200]}...")
            
        return "\n".join(results) if results else "No external resources found."
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return f"Error searching for external resources: {str(e)}"

def is_capable_model(model: Any) -> bool:
    # Requirement 1 helper
    model_name = ""
    if hasattr(model, 'model_name'):
        model_name = model.model_name
    elif isinstance(model, str):
        model_name = model
    else:
        model_name = str(model)
    
    capable_prefixes = ('gpt-4o', 'gemini', 'claude')
    return any(p in model_name.lower() for p in capable_prefixes)

def parse_agent_recommendation(text: str) -> AgentRecommendation:
    # Requirement 1 helper
    try:
        data = json.loads(text)
        return AgentRecommendation(**data)
    except (json.JSONDecodeError, ValueError) as e:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             try:
                 data = json.loads(match.group())
                 return AgentRecommendation(**data)
             except Exception as inner_e:
                 raise ValueError(f"Found JSON but failed validation: {inner_e}") from inner_e
        raise ValueError(f"Could not parse AgentRecommendation from LLM output: {text}") from e
