from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.infrastructure.db.models import LearningPlanORM
from app.domain.recommendation.entities import LearningPlan, LearningPathStep


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_plan(self, user_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .where(LearningPlanORM.is_active == True)  # noqa: E712
        )
        if not o:
            return None

        # steps is stored as JSON, need to map to LearningPathStep
        steps = [LearningPathStep(**step) for step in o.steps]

        return LearningPlan(
            id=o.id, goal=o.goal, steps=steps, is_active=o.is_active
        )

    def create_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        # Map steps to dict for JSON storage
        steps_data = [
            {
                "order": s.order,
                "title": s.title,
                "description": s.description,
                "resource_id": s.resource_id,
                "is_external": s.is_external,
            }
            for s in plan.steps
        ]

        db_plan = LearningPlanORM(
            user_id=user_id,
            goal=plan.goal,
            steps=steps_data,
            is_active=plan.is_active,
        )
        self.db.add(db_plan)
        self.db.commit()
        self.db.refresh(db_plan)

        return LearningPlan(
            id=db_plan.id,
            goal=db_plan.goal,
            steps=plan.steps,
            is_active=db_plan.is_active,
        )

    def deactivate_all_plans(self, user_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.user_id == user_id)
            .values(is_active=False)
        )
        self.db.commit()
