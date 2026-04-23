import asyncio
import logging
from dataclasses import asdict
from app.domain.recommendation.entities import Student, ModelProvider
from app.domain.catalog.entities import Course
from app.infrastructure.ai.agent import get_recommendation_agent, get_model, parse_agent_recommendation, AgentRecommendation

logger = logging.getLogger(__name__)

async def run_agent_task(ctx: dict, student_dict: dict, course_dict: dict, provider_name: str) -> dict:
    try:
        # Convert dicts back to domain entities
        student = Student(**student_dict)
        course = Course(**course_dict)
        provider = ModelProvider(provider_name)
        
        llm = get_model(provider)
        agent = get_recommendation_agent(llm, student, course)
        
        response = await agent.run(user_msg="Evaluate how well this course fits the student and provide your recommendation in JSON format.")
        
        result = parse_agent_recommendation(str(response))
        # Return as dict for serialization
        return {
            "score": result.score,
            "reasoning": result.reasoning,
            "tags": result.tags
        }
    except Exception as e:
        logger.error(f"Error in run_agent_task: {e}", exc_info=True)
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "failed"
        }
