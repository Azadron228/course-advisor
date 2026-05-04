from app.infrastructure.db.models import LearningPlanORM, LessonORM
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

def test_lesson_isolation_between_plans(db: Session):
    repo = PlanRepository(db)
    
    # 1. Create two plans
    plan1 = LearningPlan(goal="Plan 1", steps=[Lesson(order=1, title="L1", description="D1")], is_active=True)
    plan2 = LearningPlan(goal="Plan 2", steps=[Lesson(order=1, title="L2", description="D2")], is_active=False)
    
    saved_plan1 = repo.create_plan(user_id=1, plan=plan1)
    saved_plan2 = repo.create_plan(user_id=1, plan=plan2)
    
    assert len(saved_plan1.steps) == 1
    assert len(saved_plan2.steps) == 1
    
    # 2. Update Plan 1
    updated_plan1 = saved_plan1.model_copy(update={
        "steps": [
            Lesson(order=1, title="L1 Updated", description="D1"),
            Lesson(order=2, title="L1 New", description="D1")
        ]
    })
    repo.update_plan(user_id=1, plan=updated_plan1)
    
    # 3. Verify Plan 1 has 2 lessons and Plan 2 STILL has 1 lesson
    fetched_plan1 = repo.get_by_id(user_id=1, plan_id=saved_plan1.id)
    fetched_plan2 = repo.get_by_id(user_id=1, plan_id=saved_plan2.id)
    
    assert len(fetched_plan1.steps) == 2
    assert fetched_plan1.steps[0].title == "L1 Updated"
    
    assert len(fetched_plan2.steps) == 1
    assert fetched_plan2.steps[0].title == "L2"
