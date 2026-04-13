from  app.agent import recommendation_agent, AgentRecommendation, get_model, AgentDeps, is_capable_model, parse_agent_recommendation
from  app.models import Student, Course, ModelProvider
import logging

logger = logging.getLogger(__name__)

class RAGScorer:
    async def score(self, student: Student, course: Course, provider: ModelProvider = ModelProvider.AUTO) -> AgentRecommendation:
        model = get_model(provider)
        deps = AgentDeps(student=student, course=course)
        
        # Requirement 1: Adapt output_type per model
        capable = is_capable_model(model)
        
        try:
            if capable:
                # Use Schema for capable models
                result = await recommendation_agent.run(
                    "Evaluate how well this course fits the student.",
                    model=model,
                    deps=deps,
                    output_type=AgentRecommendation
                )
                return result.output
            else:
                # Use str + manual parse for weak models
                result = await recommendation_agent.run(
                    "Evaluate how well this course fits the student. Output ONLY a valid JSON object matching the AgentRecommendation schema.",
                    model=model,
                    deps=deps,
                    output_type=str
                )
                try:
                    return parse_agent_recommendation(result.output)
                except ValueError as e:
                    # Requirement 5: Log result.all_messages() on validation errors
                    logger.error(f"Manual validation error: {e}. All messages: {result.all_messages()}")
                    raise
        except Exception as e:
            # Check if we can extract messages from the exception if it's a pydantic-ai error
            if hasattr(e, 'result') and hasattr(e.result, 'all_messages'):
                logger.error(f"Agent run failed validation: {e}. All messages: {e.result.all_messages()}")
            else:
                logger.error(f"Agent run failed with exception: {e}")
            raise
