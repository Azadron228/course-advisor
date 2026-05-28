import logging
import asyncio
from typing import List, Optional, Any

from app.domain.identity.entities import User
from app.domain.recommendation.entities import (
    Student,
    ModelProvider,
    LearningPlan,
    Lesson,
    LearningMaterial,
)
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.ai.model_factory import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis
from app.services.lesson_service import LessonService

logger = logging.getLogger(__name__)


class LearningPlanService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
        lesson_service: LessonService,
    ):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.lesson_service = lesson_service

    async def _enrich_lesson_materials(self, lesson: Any, language: str = "en"):
        """Fetches real educational materials for a lesson using Tavily."""
        try:
            # Only search if it's an external/AI lesson
            if lesson.is_external:
                # Use the search client from lesson_service
                search_client = self.lesson_service.search_client
                real_materials_data = await search_client.search_educational_materials(
                    f"{lesson.title} {lesson.description}",
                    language=language
                )
                
                if real_materials_data:
                    lesson.materials = [
                        LearningMaterial(**m) for m in real_materials_data
                    ]
        except Exception as e:
            logger.error(f"Failed to enrich materials for lesson '{lesson.title}': {e}")

    async def generate_plan(
        self, user: User, request: Optional[Any] = None, arq_pool: Optional[Any] = None
    ) -> LearningPlan:
        """
        Generate a learning plan for a user using AI analysis of their profile.
        Saves the plan to the database and returns it.
        """
        if user.id is None:
            raise ValueError("User ID cannot be None")

        # 1. Gather profile data from repositories
        skills = self.profile_repo.get_skills(user.id)

        # Use transcript from request if provided, otherwise from DB
        if request and hasattr(request, "transcript") and request.transcript:
            transcript = request.transcript
        else:
            transcript = self.profile_repo.get_transcript(user.id)

        student = Student(
            id=str(user.id),
            name=user.full_name or "Student",
            transcript=transcript,
            current_skills=[s.skill_name for s in skills],
        )

        # 2. AI Generation via Analysis Agent (No internal courses anymore)
        llm = get_model(ModelProvider.AUTO)

        goal = request.goal if request else (user.career_goal or "General Growth")
        skill_level = request.skill_level if request else "Beginner"
        learning_style = request.learning_style if request else "Practical"
        study_time = request.study_time if request else 10
        interests = request.interests if request else []
        language = request.language if request and hasattr(request, "language") else "en"

        goal_msg = (
            f"Goal: {goal}. "
            f"Skill level: {skill_level}. Learning style: {learning_style}. "
            f"Study time: {study_time} hours/week. Interests: {', '.join(interests)}."
        )

        logger.info(f"Generating learning plan for goal: {goal}")
        try:
            parsed = await generate_global_analysis(llm, student, [], goal_msg, language)
            logger.info(f"Successfully generated analysis for {goal}")

            # Use AI generated title if available
            final_title = parsed.title if hasattr(parsed, "title") else goal

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

            # Ensure the first step is 'current' so it's not locked
            if learning_path:
                # Sort by order just in case the LLM didn't
                learning_path.sort(key=lambda x: x.order)
                learning_path[0].status = "current"
                
                # Enrich with real materials from Tavily in parallel
                enrich_tasks = [
                    self._enrich_lesson_materials(lesson, language) 
                    for lesson in learning_path
                ]
                await asyncio.gather(*enrich_tasks)
        except Exception as gen_err:
            logger.error(f"AI Generation failed: {gen_err}")
            raise

        # 3. Save the plan
        try:
            self.plan_repo.deactivate_all_plans(user.id)

            # Ensure the first non-completed step is 'current'
            found_current = False
            for step in learning_path:
                if step.status != "completed":
                    if not found_current:
                        step.status = "current"
                        found_current = True
                    else:
                        step.status = "upcoming"

            # Initial create
            initial_plan = LearningPlan(
                id=None,
                goal=final_title,
                steps=learning_path,
                is_active=True,
                skill_level=skill_level,
                learning_style=learning_style,
                study_time=study_time,
                interests=interests,
                language=language,
            )
            saved_plan = self.plan_repo.create_plan(user.id, initial_plan)
            logger.info(f"Successfully saved learning plan {saved_plan.id}")

            self.plan_repo.db.commit()
            return saved_plan
        except Exception as db_err:
            logger.error(f"Failed to persist learning plan: {db_err}")
            raise

    def list_plans(self, user_id: int) -> List[Any]:
        return self.plan_repo.get_all_summaries(user_id)

    def get_plan_detail(self, user_id: int, plan_id: int) -> Any:
        plan = self.plan_repo.get_plan_detail(user_id, plan_id)
        if not plan:
            return None
        return plan

    def delete_plan(self, user_id: int, plan_id: int) -> bool:
        return self.plan_repo.delete_plan(user_id, plan_id)

    async def get_step_detail(self, user: User, plan_id: int, step_order: int) -> Any:
        # Check ownership to distinguish between 404 and 403
        from app.infrastructure.db.models import LearningPlanORM
        from sqlalchemy import select
        plan_orm = self.plan_repo.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == plan_id))
        if plan_orm and plan_orm.user_id != user.id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to access this plan")

        # First find the lesson by order
        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None

        # Delegate to LessonService to handle content generation and full detail retrieval
        lesson = await self.lesson_service.get_lesson_detail(user, lesson_orm.id)
        if not lesson:
            return None

        self.plan_repo.touch_plan(plan_id)
        return lesson

    def update_plan_step(
        self, user_id: int, plan_id: int, step_order: int, new_status: str
    ) -> Optional[LearningPlan]:
        from app.infrastructure.db.models import LearningPlanORM
        from sqlalchemy import select
        from fastapi import HTTPException

        plan_orm = self.plan_repo.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == plan_id))
        if plan_orm and plan_orm.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this plan")

        plan = self.plan_repo.get_by_id(user_id, plan_id)
        if not plan:
            return None

        lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
        if not lesson_orm:
            return None

        # Create a mock user for LessonService (since it expects User object)
        from app.domain.identity.entities import User as DomainUser
        user = DomainUser(id=user_id, email="", hashed_password="") # minimal user for status update

        success = self.lesson_service.update_lesson_status(user, lesson_orm.id, new_status)
        if not success:
            return None

        self.plan_repo.touch_plan(plan_id)
        return self.plan_repo.get_by_id(user_id, plan_id)

    async def get_step_test(self, user: User, plan_id: int, step_order: int) -> Any:
        from app.infrastructure.db.models import LearningPlanORM
        from sqlalchemy import select
        from fastapi import HTTPException

        plan_orm = self.plan_repo.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == plan_id))
        if plan_orm and plan_orm.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this plan")

        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None

        return await self.lesson_service.get_practice_test(user, lesson_orm.id)

    async def submit_step_test(self, user: User, plan_id: int, step_order: int, submission: Any) -> Any:
        from app.infrastructure.db.models import LearningPlanORM
        from sqlalchemy import select
        from fastapi import HTTPException

        plan_orm = self.plan_repo.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == plan_id))
        if plan_orm and plan_orm.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this plan")

        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None

        return await self.lesson_service.submit_test(user, lesson_orm.id, submission)

    async def check_step_answer(self, user: User, plan_id: int, step_order: int, request: Any) -> Any:
        from app.infrastructure.db.models import LearningPlanORM
        from sqlalchemy import select
        from fastapi import HTTPException

        plan_orm = self.plan_repo.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == plan_id))
        if plan_orm and plan_orm.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this plan")

        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None

        return await self.lesson_service.check_answer(user, lesson_orm.id, request)

