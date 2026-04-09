import os
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic import BaseModel, Field

class AgentRecommendation(BaseModel):
    score: float = Field(ge=0, le=1, description="Relevance score from 0 to 1")
    reasoning: str = Field(description="Brief explanation of why this course was recommended")
    tags: list[str] = Field(description="Short tags describing the fit, e.g., 'Matches interests', 'Fills gap'")

# Define the agent
model = 'openai:gpt-4o'
if not os.getenv("OPENAI_API_KEY"):
    model = TestModel()

recommendation_agent = Agent(
    model, 
    system_prompt=(
        "You are a professional university advisor. "
        "Your task is to analyze a student's transcript and current skills "
        "against a specific course description and its taught skills. "
        "Provide a relevance score (0-1), a concise reasoning, and descriptive tags. "
        "Consider if the course adds new value or complements existing knowledge."
    )
)
