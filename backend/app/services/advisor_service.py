import logging
from typing import List
from app.domain.recommendation.entities import (
    Student, UserPreference, RecommendationResponse, 
    RecommendationResult, ScoreBreakdown, ModelProvider
)
from app.domain.catalog.entities import Course
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.domain.recommendation.scoring import ScoringService
from app.infrastructure.ai.embeddings import get_embedding
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import get_analysis_agent, parse_global_analysis

# We might want to move RAG scoring logic to a domain-friendly infrastructure service
from app.infrastructure.ai.rag import RAGScorer 

logger = logging.getLogger(__name__)

class AdvisorService:
    def __init__(
        self, 
        course_repo: CourseRepository,
        scoring_service: ScoringService
    ):
        self.course_repo = course_repo
        self.scoring_service = scoring_service
        self.rag_scorer = RAGScorer() # Temporary until fully refactored

    async def recommend(
        self,
        student: Student,
        courses: List[Course],
        preference: UserPreference,
        provider: ModelProvider = ModelProvider.AUTO
    ) -> RecommendationResponse:
        results = []
        
        # Aggregate transcript subject names for embedding
        subjects = [entry.subject_name for entry in student.transcript]
        aggregated_text = " ".join(subjects)
        student_embedding = get_embedding(aggregated_text) if subjects else []

        for course in courses:
            content_sim = 0.0
            if student_embedding:
                content_sim = self.course_repo.get_content_similarity(course.id, student_embedding)
            
            skill_gap = self.scoring_service.calculate_skill_gap(student, course)
            pref_score = self.scoring_service.calculate_preference_score(course, preference)
            
            # TODO: Refactor RAGScorer to be an infrastructure service
            # For now, we use a mock-like or temporary call
            rag_result = await self.rag_scorer.score(self.course_repo.db, student, course, provider)
            
            total_score = self.scoring_service.combine_scores(
                content_sim=content_sim,
                skill_gap=skill_gap,
                rag_score=rag_result.score,
                pref_score=pref_score,
                course=course
            )
            
            breakdown = ScoreBreakdown(
                skill_gap=skill_gap,
                content_sim=content_sim,
                preference=pref_score,
                rag_reasoning=rag_result.score,
                difficulty=course.difficulty,
                load=course.workload
            )
            
            results.append(RecommendationResult(
                course_id=course.id,
                subject_name=course.subject_name,
                score=total_score,
                breakdown=breakdown,
                reasoning=rag_result.reasoning,
                reason_tags=rag_result.tags
            ))
            
        results.sort(key=lambda x: x.score, reverse=True)
        
        analysis_data = None
        learning_path = []
        
        try:
            llm = get_model(provider)
            # Adapt domain courses back to what analysis_agent expects if needed, 
            # or refactor analysis_agent to take domain entities.
            agent = get_analysis_agent(llm, student, courses)
            
            response = await agent.run(user_msg="Perform global analysis and output JSON.")
            parsed = parse_global_analysis(str(response))
            analysis_data = parsed.skill_gap_analysis
            learning_path = parsed.learning_path
        except Exception as e:
            logger.error(f"Global analysis failed: {e}")

        return RecommendationResponse(
            results=results,
            skill_gap_analysis=analysis_data,
            learning_path=learning_path
        )
