import logging
from typing import List, Optional, Any

from app.domain.identity.entities import User
from app.domain.recommendation.entities import (
    Student,
    ModelProvider,
    LearningPlan,
)
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis

logger = logging.getLogger(__name__)


class LearningPlanService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
    ):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo

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

            # Ensure the first step is 'current' so it's not locked
            if parsed.learning_path:
                # Sort by order just in case the LLM didn't
                parsed.learning_path.sort(key=lambda x: x.order)
                parsed.learning_path[0].status = "current"
        except Exception as gen_err:
            logger.error(f"AI Generation failed: {gen_err}")
            raise

        # 3. Save the plan
        try:
            self.plan_repo.deactivate_all_plans(user.id)

            # Ensure the first non-completed step is 'current'
            found_current = False
            for step in parsed.learning_path:
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
                steps=parsed.learning_path,
                is_active=True,
                skill_level=skill_level,
                learning_style=learning_style,
                study_time=study_time,
                interests=interests,
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

    def get_step_detail(self, user_id: int, plan_id: int, step_order: int) -> Any:
        # First find the lesson by order
        lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
        if not lesson_orm:
            return None

        lesson = self.plan_repo.get_lesson_with_materials(user_id, plan_id, lesson_orm.id)
        if not lesson:
            return None

        self.plan_repo.touch_plan(plan_id)
        return lesson

    def update_plan_step(
        self, user_id: int, plan_id: int, step_order: int, new_status: str
    ) -> Optional[LearningPlan]:
        plan = self.plan_repo.get_by_id(user_id, plan_id)
        if not plan:
            return None

        if new_status == "completed":
            lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
            if not lesson_orm:
                return None
            self.plan_repo.complete_lesson(user_id, lesson_orm.id)
        else:
            # Update the specific step status
            updated_steps = sorted(plan.steps, key=lambda x: x.order)
            found_idx = -1
            for i, step in enumerate(updated_steps):
                if step.order == step_order:
                    updated_steps[i] = step.model_copy(update={"status": new_status})
                    found_idx = i
                    break

            if found_idx == -1:
                return None

            updated_plan = plan.model_copy(update={"steps": updated_steps})
            self.plan_repo.update_plan(user_id, updated_plan)

        self.plan_repo.touch_plan(plan_id)
        return self.plan_repo.get_by_id(user_id, plan_id)
