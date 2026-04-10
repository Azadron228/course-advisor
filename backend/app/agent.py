import os
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic import BaseModel, Field
from  app.models import ModelProvider

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
        # GoogleModel automatically uses GOOGLE_API_KEY from env
        return GoogleModel(
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
        )

    if provider == ModelProvider.OLLAMA:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        provider_obj = OpenAIProvider(
            base_url=f"{base_url}/v1",
            api_key='ollama', # Placeholder for local models
        )
        return OpenAIChatModel(
            model_name='llama3',
            provider=provider_obj,
        )
    
    if provider == ModelProvider.OPENAI:
        # OpenAIChatModel automatically uses OPENAI_API_KEY from env
        if not os.getenv("OPENAI_API_KEY"):
            return TestModel()
        return OpenAIChatModel('gpt-4o')

    return TestModel()

# Define the agent shell (model is passed during run)
recommendation_agent = Agent(
    TestModel(), # Placeholder, overwritten in run
    system_prompt=(
        "You are a professional university advisor. "
        "Your task is to analyze a student's transcript and current skills "
        "against a specific course description and its taught skills. "
        "Provide a relevance score (0-1), a concise reasoning, and descriptive tags. "
        "Consider if the course adds new value or complements existing knowledge."
    )
)
