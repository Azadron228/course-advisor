import logging
from app.domain.recommendation.entities import (
    Student,
    ModelProvider,
    UserPreference,
    TranscriptEntry,
)
from app.services.advisor_service import AdvisorService
from app.api.v1.schemas.recommendations import RecommendationResponse
from app.core.container import get_container

logger = logging.getLogger(__name__)


async def run_hybrid_recommendation(
    ctx: dict, student_dict: dict, preference_dict: dict, provider_name: str = "auto"
) -> dict:
    try:
        transcript = [TranscriptEntry(**entry) for entry in student_dict.get("transcript", [])]
        student = Student(
            id=student_dict["id"],
            name=student_dict["name"],
            transcript=transcript,
            current_skills=student_dict["current_skills"],
        )
        preference = UserPreference(**preference_dict)
        provider = ModelProvider(provider_name)

        container = get_container()
        advisor_service = container.resolve(AdvisorService)

        domain_response = await advisor_service.recommend(
            student, [], preference, provider=provider
        )

        schema_response = RecommendationResponse.model_validate(domain_response)
        return schema_response.model_dump()
    except Exception as e:
        logger.error(f"Error in run_hybrid_recommendation task: {e}", exc_info=True)
        return {"error": str(e), "error_type": type(e).__name__, "status": "failed"}
