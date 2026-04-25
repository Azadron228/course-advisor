import logging
from typing import List, Optional
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    RecommendationResponse,
    RecommendationResult,
    ScoreBreakdown,
    ModelProvider,
    LearningPlan,
    SkillNode,
    SkillMapResponse,
)
from app.domain.catalog.entities import Course
from app.domain.identity.entities import User
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
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

    async def generate_learning_plan(self, user: User) -> LearningPlan:
        """
        Generate a learning plan for a user using AI analysis of their profile and available courses.
        Saves the plan to the database and returns it.
        """
        # 1. Gather profile data from repositories
        skills = self.profile_repo.get_skills(user.id)
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
        agent = get_analysis_agent(llm, student, courses)

        goal_msg = f"Generate a structured learning path for career goal: {user.career_goal or 'General Growth'}. Output JSON."
        response = await agent.run(user_msg=goal_msg)
        parsed = parse_global_analysis(str(response))

        # 4. Persist the new plan
        new_plan = LearningPlan(
            id=None,
            goal=user.career_goal or "General Growth",
            steps=parsed.learning_path,
            is_active=True,
        )

        self.plan_repo.deactivate_all_plans(user.id)
        saved_plan = self.plan_repo.create_plan(user.id, new_plan)

        return saved_plan

    def get_skill_map(self, user_id: int) -> SkillMapResponse:
        """
        Derives a skill map (nodes for visualization) from the user's stored skills.
        """
        user_skills = self.profile_repo.get_skills(user_id)

        nodes = [
            SkillNode(
                id=s.skill_name.lower().replace(" ", "_"),
                label=s.skill_name,
                mastery_level=s.mastery_level,
                category=s.category,
            )
            for s in user_skills
        ]

        return SkillMapResponse(nodes=nodes)

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
            preference = UserPreference(
                interest_tags=[], target_difficulty=0.5, max_workload=0.5
            )

        # Aggregate transcript subject names for embedding
        subjects = [entry.subject_name for entry in student.transcript]
        aggregated_text = " ".join(subjects)
        student_embedding = get_embedding(aggregated_text) if subjects else []

        for course in courses:
            content_sim = 0.0
            if student_embedding:
                content_sim = self.course_repo.get_content_similarity(
                    course.id, student_embedding
                )

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
                difficulty=course.difficulty,
                load=course.workload,
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
            learning_path=learning_path,
        )
