import logging
from typing import List, Optional, Any
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    RecommendationResponse,
    ModelProvider,
)
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis

logger = logging.getLogger(__name__)


class AdvisorService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
    ):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo

    async def recommend(
        self,
        student: Student,
        courses: Optional[List[Any]] = None,
        preference: Optional[UserPreference] = None,
        provider: ModelProvider = ModelProvider.AUTO,
        language: str = "en",
    ) -> RecommendationResponse:
        if preference is None:
            preference = UserPreference(interest_tags=[])

        analysis_data = None
        learning_path = []

        try:
            llm = get_model(provider)
            goal_msg = f"Recommendation interests: {', '.join(preference.interest_tags)}"
            parsed = await generate_global_analysis(llm, student, [], goal_msg, language)

            analysis_data = parsed.skill_gap_analysis
            learning_path = parsed.learning_path

            # Sort and Resolve IDs for recommendation path too
            if learning_path:
                learning_path.sort(key=lambda x: x.order)

                # Make the first one current so it's not locked in preview
                learning_path[0].status = "current"
        except Exception as e:
            logger.error(f"Global analysis failed: {e}")

        return RecommendationResponse(
            results=[],
            skill_gap_analysis=analysis_data,
            learning_path=learning_path,
        )
