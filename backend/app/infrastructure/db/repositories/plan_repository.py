from __future__ import annotations
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload
from app.infrastructure.db.models import LearningPlanORM, LessonORM, UserTestScoreORM
from app.domain.recommendation.entities import LearningPlan, Lesson, LearningMaterial


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, o: LearningPlanORM) -> LearningPlan:
        # Collect lesson IDs for scores
        lesson_ids = [l.id for l in o.lessons]
        
        scores_map = {}
        if lesson_ids:
            scores = self.db.execute(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == o.user_id)
                .where(UserTestScoreORM.lesson_id.in_(lesson_ids))
            ).scalars().all()
            scores_map = {s.lesson_id: s.score for s in scores}

        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[
                Lesson(
                    id=l.id,
                    order=l.order,
                    title=l.title,
                    description=l.description,
                    resource_id=str(l.material_id) if l.material_id else None,
                    is_external=l.is_external,
                    external_url=l.external_url,
                    content=l.content,
                    status=l.status,
                    materials=[LearningMaterial(**m) for m in l.additional_resources],
                    score=scores_map.get(l.id)
                ) 
                for l in o.lessons
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
            interests=plan.interests
        )
        self.db.add(db_plan)
        self.db.flush() # Get ID

        for s in plan.steps:
            lesson = LessonORM(
                plan_id=db_plan.id,
                order=s.order,
                title=s.title,
                description=s.description,
                material_id=int(s.resource_id) if s.resource_id and not s.is_external else None,
                is_external=s.is_external,
                external_url=s.external_url,
                content=s.content,
                status=s.status,
                additional_resources=[m.model_dump() for m in s.materials]
            )
            self.db.add(lesson)
        
        self.db.commit()
        
        # Re-fetch with lessons to be sure
        return self.get_by_id(user_id, db_plan.id)

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
        from sqlalchemy import delete
        self.db.execute(delete(LessonORM).where(LessonORM.plan_id == o.id))
        self.db.flush()

        for s in plan.steps:
            lesson = LessonORM(
                plan_id=o.id,
                order=s.order,
                title=s.title,
                description=s.description,
                material_id=int(s.resource_id) if s.resource_id and not s.is_external else None,
                is_external=s.is_external,
                external_url=s.external_url,
                content=s.content,
                status=s.status,
                additional_resources=[m.model_dump() for m in s.materials]
            )
            self.db.add(lesson)

        self.db.commit()
        return self.get_by_id(user_id, o.id)

    def deactivate_all_plans(self, user_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .values(is_active=False)
        )
        self.db.commit()

    def update_lesson_status(self, lesson_id: int, status: str) -> bool:
        result = self.db.execute(
            update(LessonORM)
            .where(LessonORM.id == lesson_id)
            .values(status=status)
        )
        self.db.commit()
        return result.rowcount > 0

    def get_lesson(self, lesson_id: int) -> Optional[LessonORM]:
        return self.db.scalar(
            select(LessonORM).where(LessonORM.id == lesson_id)
        )

    def get_all_summaries(self, user_id: int) -> List[LearningPlanSummary]:
        from sqlalchemy import func
        from app.api.v1.schemas.recommendations import LearningPlanSummary
        
        # Subquery to count lessons per plan
        count_subquery = (
            select(LessonORM.plan_id, func.count(LessonORM.id).label("step_count"))
            .group_by(LessonORM.plan_id)
            .subquery()
        )

        query = (
            select(LearningPlanORM, count_subquery.c.step_count)
            .outerjoin(count_subquery, LearningPlanORM.id == count_subquery.c.plan_id)
            .where(LearningPlanORM.user_id == user_id)
            .order_by(LearningPlanORM.last_interacted_at.desc())
        )
        
        results = self.db.execute(query).all()
        
        return [
            LearningPlanSummary(
                id=p.id,
                goal=p.goal,
                is_active=p.is_active,
                last_interacted_at=p.last_interacted_at,
                step_count=step_count or 0
            )
            for p, step_count in results
        ]

    def get_plan_detail(self, user_id: int, plan_id: int) -> Optional[LearningPlanDetail]:
        from app.api.v1.schemas.recommendations import LearningPlanDetail, LessonSummary
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return None
            
        # Collect lesson IDs for scores
        lesson_ids = [l.id for l in o.lessons]
        scores_map = {}
        if lesson_ids:
            scores = self.db.execute(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == user_id)
                .where(UserTestScoreORM.lesson_id.in_(lesson_ids))
            ).scalars().all()
            scores_map = {s.lesson_id: s.score for s in scores}

        return LearningPlanDetail(
            id=o.id,
            goal=o.goal,
            is_active=o.is_active,
            last_interacted_at=o.last_interacted_at,
            steps=[
                LessonSummary(
                    id=l.id,
                    order=l.order,
                    title=l.title,
                    description=l.description,
                    status=l.status,
                    is_external=l.is_external,
                    score=scores_map.get(l.id)
                )
                for l in o.lessons
            ]
        )

    def get_lesson_with_materials(self, user_id: int, plan_id: int, lesson_id: int) -> Optional[LessonDetail]:
        from app.api.v1.schemas.recommendations import LessonDetail, LearningMaterial
        l = self.db.scalar(
            select(LessonORM)
            .join(LearningPlanORM)
            .where(LessonORM.id == lesson_id)
            .where(LessonORM.plan_id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not l:
            return None

        score = None
        score_rec = self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )
        score = score_rec.score if score_rec else None

        return LessonDetail(
            id=l.id,
            order=l.order,
            title=l.title,
            description=l.description,
            status=l.status,
            is_external=l.is_external,
            external_url=l.external_url,
            content=l.content,
            score=score,
            materials=[LearningMaterial(**m) for m in l.additional_resources]
        )

    def get_lesson_by_order(self, user_id: int, plan_id: int, order: int) -> Optional[LessonORM]:
        return self.db.scalar(
            select(LessonORM)
            .join(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .where(LessonORM.plan_id == plan_id)
            .where(LessonORM.order == order)
        )

    def touch_plan(self, plan_id: int):
        from datetime import datetime, timezone
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .values(last_interacted_at=datetime.now(timezone.utc))
        )
        self.db.commit()
