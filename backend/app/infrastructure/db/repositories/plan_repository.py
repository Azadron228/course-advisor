from typing import Optional, List
from dataclasses import asdict
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.infrastructure.db.models import LearningPlanORM
from app.domain.recommendation.entities import LearningPlan, LearningPathStep, LearningMaterial


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, o: LearningPlanORM) -> LearningPlan:
        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[
                LearningPathStep(
                    **{k: v for k, v in step.items() if k != "materials"},
                    materials=[LearningMaterial(**m) for m in step.get("materials", [])]
                ) 
                for step in o.steps
            ],
            is_active=o.is_active,
            skill_level=o.skill_level,
            learning_style=o.learning_style,
            study_time=o.study_time,
            interests=o.interests,
        )

    def get_all_plans(self, user_id: int) -> List[LearningPlan]:
        objs = self.db.scalars(
            select(LearningPlanORM).where(LearningPlanORM.user_id == user_id)
        ).all()
        return [self._to_domain(o) for o in objs]

    def get_by_id(self, user_id: int, plan_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return None
        return self._to_domain(o)

    def get_active_plan(self, user_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .where(LearningPlanORM.is_active == True)  # noqa: E712
        )
        if not o:
            return None

        return self._to_domain(o)

    def create_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        # Map steps to dict for JSON storage
        steps_data = [
            {
                "order": s.order,
                "title": s.title,
                "description": s.description,
                "resource_id": s.resource_id,
                "is_external": s.is_external,
                "status": s.status,
                "materials": [asdict(m) for m in s.materials]
            }
            for s in plan.steps
        ]

        db_plan = LearningPlanORM(
            user_id=user_id,
            goal=plan.goal,
            steps=steps_data,
            is_active=plan.is_active,
            skill_level=plan.skill_level,
            learning_style=plan.learning_style,
            study_time=plan.study_time,
            interests=plan.interests
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        return LearningPlan(
            id=db_plan.id,
            goal=db_plan.goal,
            steps=plan.steps,
            is_active=db_plan.is_active,
            skill_level=db_plan.skill_level,
            learning_style=db_plan.learning_style,
            study_time=db_plan.study_time,
            interests=db_plan.interests
        )

    def update_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.id == plan.id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            raise Exception("Learning plan not found")

        # Map steps to dict for JSON storage
        steps_data = [
            {
                "order": s.order,
                "title": s.title,
                "description": s.description,
                "resource_id": s.resource_id,
                "is_external": s.is_external,
                "status": s.status,
                "materials": [asdict(m) for m in s.materials]
            }
            for s in plan.steps
        ]

        o.goal = plan.goal
        o.steps = steps_data
        o.is_active = plan.is_active
        o.skill_level = plan.skill_level
        o.learning_style = plan.learning_style
        o.study_time = plan.study_time
        o.interests = plan.interests

        self.db.commit()
        self.db.refresh(o)
        return plan

    def deactivate_all_plans(self, user_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .values(is_active=False)
        )
        self.db.commit()
