from app.infrastructure.db.models import LearningPlanORM, LessonORM, CourseMaterialORM
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.domain.recommendation.entities import LearningPlan, Lesson

def test_lessons_relationship(db: Session):
    # 1. Create a plan
    plan = LearningPlanORM(
        user_id=1,
        goal="Test Goal",
        is_active=True
    )
    db.add(plan)
    db.flush()

    # 2. Add lessons
    lesson1 = LessonORM(
        plan_id=plan.id,
        order=1,
        title="Lesson 1",
        description="Desc 1",
        status="current"
    )
    lesson2 = LessonORM(
        plan_id=plan.id,
        order=2,
        title="Lesson 2",
        description="Desc 2",
        status="upcoming"
    )
    db.add_all([lesson1, lesson2])
    db.commit()

    # 3. Verify relationship
    db.refresh(plan)
    assert len(plan.lessons) == 2
    assert plan.lessons[0].title == "Lesson 1"
    assert plan.lessons[1].title == "Lesson 2"
    assert plan.lessons[0].order == 1
    assert plan.lessons[1].order == 2

def test_plan_repository_create_and_get(db: Session):
    repo = PlanRepository(db)
    
    domain_plan = LearningPlan(
        goal="Repo Test",
        steps=[
            Lesson(order=1, title="L1", description="D1", status="current"),
            Lesson(order=2, title="L2", description="D2", status="upcoming")
        ],
        is_active=True
    )
    
    saved_plan = repo.create_plan(user_id=1, plan=domain_plan)
    assert saved_plan.id is not None
    assert len(saved_plan.steps) == 2
    assert saved_plan.steps[0].title == "L1"
    
    # Get by ID
    fetched_plan = repo.get_by_id(user_id=1, plan_id=saved_plan.id)
    assert fetched_plan is not None
    assert len(fetched_plan.steps) == 2
    assert fetched_plan.steps[1].description == "D2"

def test_lesson_status_update(db: Session):
    repo = PlanRepository(db)
    
    # Setup
    plan = LearningPlanORM(user_id=1, goal="Status Test")
    db.add(plan)
    db.flush()
    lesson = LessonORM(plan_id=plan.id, order=1, title="L", description="D", status="upcoming")
    db.add(lesson)
    db.commit()
    
    # Update status
    repo.update_lesson_status(lesson.id, "completed")
    
    # Verify
    db.refresh(lesson)
    assert lesson.status == "completed"
