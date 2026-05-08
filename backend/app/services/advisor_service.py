import logging
from typing import List, Optional, Any
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    RecommendationResponse,
    RecommendationResult,
    ScoreBreakdown,
    ModelProvider,
)
from app.domain.catalog.entities import Course
from app.domain.identity.entities import User
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.domain.recommendation.scoring import ScoringService
from app.infrastructure.ai.embeddings import get_embedding
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis

# We might want to move RAG scoring logic to a domain-friendly infrastructure service
from app.infrastructure.ai.rag import RAGScorer

logger = logging.getLogger(__name__)


class AdvisorService:
    def __init__(
        self,
        course_repo: CourseRepository,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
        scoring_service: ScoringService,
        rag_scorer: RAGScorer,
    ):
        self.course_repo = course_repo
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.scoring_service = scoring_service
        self.rag_scorer = rag_scorer

    async def recommend(
        self,
        student: Student,
        courses: Optional[List[Course]] = None,
        preference: Optional[UserPreference] = None,
        provider: ModelProvider = ModelProvider.AUTO,
        language: str = "en",
    ) -> RecommendationResponse:
        results = []

        if courses is None:
            courses = self.course_repo.get_all()

        if preference is None:
            preference = UserPreference(interest_tags=[])

        # Aggregate transcript subject names for embedding
        subjects = [entry.subject_name for entry in student.transcript]
        aggregated_text = " ".join(subjects)
        student_embedding = get_embedding(aggregated_text) if subjects else []

        for course in courses:
            content_sim = 0.0
            if student_embedding:
                # 1. Broad match (Description)
                desc_sim = self.course_repo.get_content_similarity(course.id, student_embedding)
                
                # 2. Granular match (Best Material Chunk)
                chunk_sim = self.course_repo.get_best_material_similarity(course.id, student_embedding)
                
                # Final content similarity is the best match found
                content_sim = max(desc_sim, chunk_sim)

            skill_gap = self.scoring_service.calculate_skill_gap(student, course)
            pref_score = self.scoring_service.calculate_preference_score(
                course, preference
            )

            rag_result = await self.rag_scorer.score(
                self.course_repo.db, student, course, provider
            )

            total_score = self.scoring_service.combine_scores(
                content_sim=content_sim,
                skill_gap=skill_gap,
                rag_score=rag_result.score,
                pref_score=pref_score,
                course=course,
            )

            breakdown = ScoreBreakdown(
                skill_gap=skill_gap,
                content_sim=content_sim,
                preference=pref_score,
                rag_reasoning=rag_result.score,
            )

            results.append(
                RecommendationResult(
                    course_id=course.id,
                    subject_name=course.subject_name,
                    score=total_score,
                    breakdown=breakdown,
                    reasoning=rag_result.reasoning,
                    reason_tags=rag_result.tags,
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)

        analysis_data = None
        learning_path = []

        try:
            llm = get_model(provider)
            goal_msg = f"Recommendation interests: {', '.join(preference.interest_tags)}"
            parsed = await generate_global_analysis(llm, student, courses, goal_msg, language)
            
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
            results=results,
            skill_gap_analysis=analysis_data,
            learning_path=learning_path,
        )
