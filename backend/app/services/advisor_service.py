import logging
from typing import List, Optional, Any
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    RecommendationResponse,
    RecommendationResult,
    ScoreBreakdown,
    ModelProvider,
    LearningPlan,
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

    async def generate_learning_plan(self, user: User, request: Optional[Any] = None, arq_pool: Optional[Any] = None) -> LearningPlan:
        """
        Generate a learning plan for a user using AI analysis of their profile and available courses.
        Saves the plan to the database and returns it.
        """
        if user.id is None:
            raise ValueError("User ID cannot be None")

        # 1. Gather profile data from repositories
        skills = self.profile_repo.get_skills(user.id)
        
        # Use transcript from request if provided, otherwise from DB
        if request and hasattr(request, 'transcript') and request.transcript:
            transcript = request.transcript
        else:
            transcript = self.profile_repo.get_transcript(user.id)

        student = Student(
            id=str(user.id),
            name=user.full_name or "Student",
            transcript=transcript,
            current_skills=[s.skill_name for s in skills],
        )

        # 2. Get all available internal courses
        courses = self.course_repo.get_all()

        # 3. AI Generation via Analysis Agent
        llm = get_model(ModelProvider.AUTO)
        
        goal = request.goal if request else (user.career_goal or "General Growth")
        skill_level = request.skill_level if request else "Beginner"
        learning_style = request.learning_style if request else "Practical"
        study_time = request.study_time if request else 10
        interests = request.interests if request else []

        goal_msg = (
            f"Goal: {goal}. "
            f"Skill level: {skill_level}. Learning style: {learning_style}. "
            f"Study time: {study_time} hours/week. Interests: {', '.join(interests)}."
        )
        
        logger.info(f"Generating learning plan for goal: {goal}")
        try:
            parsed = await generate_global_analysis(llm, student, courses, goal_msg)
            logger.info(f"Successfully generated analysis for {goal}")
        except Exception as gen_err:
            logger.error(f"AI Generation failed: {gen_err}")
            raise

        # 4. Persist the new plan
        try:
            new_plan = LearningPlan(
                id=None,
                goal=goal,
                steps=parsed.learning_path,
                is_active=True,
                skill_level=skill_level,
                learning_style=learning_style,
                study_time=study_time,
                interests=interests,
            )

            if user.id is None:
                raise ValueError("User ID cannot be None")

            self.plan_repo.deactivate_all_plans(user.id)
            saved_plan = self.plan_repo.create_plan(user.id, new_plan)
            logger.info(f"Successfully saved learning plan {saved_plan.id}")

            # 5. Enqueue practice test generation for all internal steps
            if arq_pool:
                for step in saved_plan.steps:
                    if not step.is_external and step.resource_id:
                        try:
                            material_id = int(step.resource_id)
                            await arq_pool.enqueue_job("generate_practice_test", material_id)
                            logger.info(f"Enqueued practice test generation for material {material_id}")
                        except (ValueError, TypeError):
                            continue

            return saved_plan
        except Exception as db_err:
            logger.error(f"Failed to persist learning plan: {db_err}")
            raise

    async def recommend(
        self,
        student: Student,
        courses: Optional[List[Course]] = None,
        preference: Optional[UserPreference] = None,
        provider: ModelProvider = ModelProvider.AUTO,
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
            parsed = await generate_global_analysis(llm, student, courses, goal_msg)
            
            analysis_data = parsed.skill_gap_analysis
            learning_path = parsed.learning_path
        except Exception as e:
            logger.error(f"Global analysis failed: {e}")

        return RecommendationResponse(
            results=results,
            skill_gap_analysis=analysis_data,
            learning_path=learning_path,
        )
