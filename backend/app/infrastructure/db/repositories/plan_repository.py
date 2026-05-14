from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING, cast
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.engine import CursorResult
from app.infrastructure.db.models import (
    LearningPlanORM,
    LessonORM,
    UserTestScoreORM,
    PracticeTestORM,
)
from app.domain.recommendation.entities import LearningPlan, Lesson, LearningMaterial
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.api.v1.schemas.recommendations import (
        LearningPlanSummary,
        LearningPlanDetail,
        LessonDetail,
    )


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, o: LearningPlanORM) -> LearningPlan:
        # Collect lesson IDs for scores
        lesson_ids = [lesson.id for lesson in o.lessons]

        scores_map = {}
        if lesson_ids:
            scores = (
                self.db.execute(
                    select(UserTestScoreORM)
                    .where(UserTestScoreORM.user_id == o.user_id)
                    .where(UserTestScoreORM.lesson_id.in_(lesson_ids))
                )
                .scalars()
                .all()
            )
            scores_map = {s.lesson_id: s.score for s in scores}

        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[
                Lesson(
                    id=lesson.id,
                    order=lesson.order,
                    title=lesson.title,
                    description=lesson.description,
                    resource_id=None,
                    is_external=lesson.is_external,
                    external_url=lesson.external_url,
                    content=lesson.content,
                    status=lesson.status,
                    materials=[LearningMaterial(**m) for m in lesson.additional_resources],
                    score=scores_map.get(lesson.id),
                )
                for lesson in o.lessons
            ],
            is_active=o.is_active,
            skill_level=o.skill_level,
            learning_style=o.learning_style,
            study_time=o.study_time,
            interests=o.interests,
        )

    def get_all_plans(self, user_id: int) -> List[LearningPlan]:
        objs = self.db.scalars(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.user_id == user_id)
        ).all()
        return [self._to_domain(o) for o in objs]

    def get_by_id(self, user_id: int, plan_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return None
        return self._to_domain(o)

    def get_active_plan(self, user_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.user_id == user_id)
            .where(LearningPlanORM.is_active == True)  # noqa: E712
        )
        if not o:
            return None

        return self._to_domain(o)

    def create_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        db_plan = LearningPlanORM(
            user_id=user_id,
            goal=plan.goal,
            is_active=plan.is_active,
            skill_level=plan.skill_level,
            learning_style=plan.learning_style,
            study_time=plan.study_time,
            interests=plan.interests,
        )
        self.db.add(db_plan)
        self.db.flush()  # Get ID

        for s in plan.steps:
            lesson = LessonORM(
                plan_id=db_plan.id,
                order=s.order,
                title=s.title,
                description=s.description,
                is_external=s.is_external,
                external_url=s.external_url,
                content=s.content,
                status=s.status,
                additional_resources=[m.model_dump() for m in s.materials],
            )
            self.db.add(lesson)

        self.db.commit()

        # Re-fetch with lessons to be sure
        result = self.get_by_id(user_id, db_plan.id)
        if not result:
            raise ValueError("Failed to retrieve created plan")
        return result

    def update_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == plan.id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            raise Exception("Learning plan not found")

        o.goal = plan.goal
        o.is_active = plan.is_active
        o.skill_level = plan.skill_level
        o.learning_style = plan.learning_style
        o.study_time = plan.study_time
        o.interests = plan.interests

        # Clear existing lessons for THIS plan
        self.db.execute(delete(LessonORM).where(LessonORM.plan_id == o.id))
        self.db.flush()

        for s in plan.steps:
            lesson = LessonORM(
                plan_id=o.id,
                order=s.order,
                title=s.title,
                description=s.description,
                is_external=s.is_external,
                external_url=s.external_url,
                content=s.content,
                status=s.status,
                additional_resources=[m.model_dump() for m in s.materials],
            )
            self.db.add(lesson)

        self.db.commit()

        result = self.get_by_id(user_id, o.id)
        if not result:
            raise ValueError("Failed to retrieve updated plan")
        return result

    def deactivate_all_plans(self, user_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .values(is_active=False)
        )
        self.db.commit()

    def update_lesson_status(self, lesson_id: int, status: str) -> bool:
        result = self.db.execute(
            update(LessonORM).where(LessonORM.id == lesson_id).values(status=status)
        )
        self.db.commit()
        return cast(CursorResult, result).rowcount > 0

    def get_lesson(self, lesson_id: int) -> Optional[LessonORM]:
        return self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))

    def get_practice_test(self, lesson_id: int) -> Optional[PracticeTestORM]:
        return self.db.scalar(select(PracticeTestORM).where(PracticeTestORM.lesson_id == lesson_id))

    def create_practice_test(self, lesson_id: int, content: dict) -> PracticeTestORM:
        db_test = PracticeTestORM(lesson_id=lesson_id, content=content)
        self.db.add(db_test)
        self.db.commit()
        self.db.refresh(db_test)
        return db_test

    def save_test_score(self, user_id: int, lesson_id: int, score: int, answers: list) -> None:
        # 1. Check if user already has a score for this lesson
        existing_score = self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )

        if existing_score:
            # 2. Always update score and answers for the latest attempt
            existing_score.score = score
            existing_score.answers = {"answers": answers}
            existing_score.attempts += 1
            existing_score.completed_at = datetime.now(timezone.utc)
        else:
            # 3. Create new
            new_score = UserTestScoreORM(
                user_id=user_id,
                lesson_id=lesson_id,
                score=score,
                answers={"answers": answers},
                attempts=1,
            )
            self.db.add(new_score)

        self.db.commit()

    def get_last_test_score(self, user_id: int, lesson_id: int) -> Optional[UserTestScoreORM]:
        return self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )

    def complete_lesson(self, user_id: int, lesson_id: int):
        """Marks a lesson as completed and auto-unlocks the next one."""
        lesson = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
        if not lesson:
            return

        plan = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == lesson.plan_id)
        )
        if not plan:
            return

        lesson.status = "completed"

        # Auto-unlock next step
        found_idx = -1
        for i, lesson_item in enumerate(plan.lessons):
            if lesson_item.id == lesson.id:
                found_idx = i
                break

        if found_idx != -1 and found_idx + 1 < len(plan.lessons):
            next_lesson = plan.lessons[found_idx + 1]
            if next_lesson.status == "upcoming":
                next_lesson.status = "current"

        self.db.commit()

    def get_lesson_by_order(self, user_id: int, plan_id: int, order: int) -> Optional[LessonORM]:
        return self.db.scalar(
            select(LessonORM)
            .join(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
            .where(LessonORM.order == order)
        )

    def get_all_summaries(self, user_id: int) -> List[LearningPlanSummary]:
        from app.api.v1.schemas.recommendations import LearningPlanSummary as LPSchema

        plans = self.db.scalars(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.user_id == user_id)
            .order_by(LearningPlanORM.last_interacted_at.desc())
        ).all()

        return [
            LPSchema(
                id=p.id,
                goal=p.goal,
                is_active=p.is_active,
                last_interacted_at=p.last_interacted_at,
                step_count=len(p.lessons),
            )
            for p in plans
        ]

    def get_plan_detail(self, user_id: int, plan_id: int) -> Optional[LearningPlanDetail]:
        from app.api.v1.schemas.recommendations import (
            LearningPlanDetail as LPDetailSchema,
            LessonSummary,
        )

        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return None

        # Fetch scores
        lesson_ids = [lesson.id for lesson in o.lessons]
        scores_map = {}
        if lesson_ids:
            scores = self.db.scalars(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == user_id)
                .where(UserTestScoreORM.lesson_id.in_(lesson_ids))
            ).all()
            scores_map = {s.lesson_id: s.score for s in scores}

        return LPDetailSchema(
            id=o.id,
            goal=o.goal,
            is_active=o.is_active,
            last_interacted_at=o.last_interacted_at,
            steps=[
                LessonSummary(
                    id=lesson.id,
                    order=lesson.order,
                    title=lesson.title,
                    description=lesson.description,
                    status=lesson.status,
                    score=scores_map.get(lesson.id),
                    is_external=lesson.is_external,
                )
                for lesson in sorted(o.lessons, key=lambda x: x.order)
            ],
        )

    def get_lesson_with_materials(
        self, user_id: int, plan_id: int, lesson_id: int
    ) -> Optional[LessonDetail]:
        from app.api.v1.schemas.recommendations import (
            LessonDetail as LDetailSchema,
            LearningMaterial as LMSchema,
        )

        lesson = self.db.scalar(
            select(LessonORM)
            .join(LearningPlanORM)
            .where(LessonORM.id == lesson_id)
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not lesson:
            return None

        # Fetch score
        score = self.db.scalar(
            select(UserTestScoreORM.score)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )

        return LDetailSchema(
            id=lesson.id,
            order=lesson.order,
            title=lesson.title,
            description=lesson.description,
            status=lesson.status,
            score=score,
            is_external=lesson.is_external,
            external_url=lesson.external_url,
            content=lesson.content,
            materials=[LMSchema(**m) for m in lesson.additional_resources],
        )

    def delete_plan(self, user_id: int, plan_id: int) -> bool:
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return False

        self.db.delete(o)
        self.db.commit()
        return True

    def touch_plan(self, plan_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .values(last_interacted_at=datetime.now(timezone.utc))
        )
        self.db.commit()
