import os
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from backend.models import ModelProvider

class AgentRecommendation(BaseModel):
    score: float = Field(ge=0, le=1, description="Relevance score from 0 to 1")
    reasoning: str = Field(description="Brief explanation of why this course was recommended")
    tags: list[str] = Field(description="Short tags describing the fit, e.g., 'Matches interests', 'Fills gap'")

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
        return GeminiModel(
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if provider == ModelProvider.OLLAMA:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OpenAIModel(
            model_name='llama3',
            base_url=f"{base_url}/v1",
            api_key='ollama',
        )
    
    if provider == ModelProvider.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return TestModel()
        return OpenAIModel('gpt-4o', api_key=api_key)

    return TestModel()

# Define the agent shell (model is passed during run)
recommendation_agent = Agent(
    'gemini-1.5-flash', # Placeholder, overwritten in run
    system_prompt=(
        "You are a professional university advisor. "
        "Your task is to analyze a student's transcript and current skills "
        "against a specific course description and its taught skills. "
        "Provide a relevance score (0-1), a concise reasoning, and descriptive tags. "
        "Consider if the course adds new value or complements existing knowledge."
    )
)
