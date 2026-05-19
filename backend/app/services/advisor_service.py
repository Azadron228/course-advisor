import logging
import asyncio
from typing import List, Optional, Any
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    RecommendationResponse,
    ModelProvider,
    Lesson,
    LearningMaterial,
)
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis
from app.infrastructure.ai.tavily_search import TavilySearch

logger = logging.getLogger(__name__)


class AdvisorService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
    ):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.search_client = TavilySearch()

    async def _enrich_lesson_materials(self, lesson: Lesson, language: str = "en"):
        """Fetches real educational materials for a lesson using Tavily."""
        try:
            if lesson.is_external:
                real_materials_data = await self.search_client.search_educational_materials(
                    f"{lesson.title} {lesson.description}",
                    language=language
                )
                if real_materials_data:
                    lesson.materials = [
                        LearningMaterial(**m) for m in real_materials_data
                    ]
        except Exception as e:
            logger.error(f"Failed to enrich materials for lesson '{lesson.title}': {e}")

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
            
            # Convert LessonPlanStep to domain Lesson
            learning_path = []
            for step in parsed.learning_path:
                learning_path.append(
                    Lesson(
                        order=step.order,
                        title=step.title,
                        description=step.description,
                        is_external=step.is_external,
                        status="upcoming",
                        materials=[],
                    )
                )

            # Sort and Resolve IDs for recommendation path too
            if learning_path:
                learning_path.sort(key=lambda x: x.order)

                # Make the first one current so it's not locked in preview
                learning_path[0].status = "current"
                
                # Enrich with real materials from Tavily in parallel
                enrich_tasks = [
                    self._enrich_lesson_materials(lesson, language) 
                    for lesson in learning_path
                ]
                await asyncio.gather(*enrich_tasks)
        except Exception as e:
            logger.error(f"Global analysis failed: {e}")

        return RecommendationResponse(
            results=[],
            skill_gap_analysis=analysis_data,
            learning_path=learning_path,
        )
