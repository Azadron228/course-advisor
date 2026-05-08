from sqlalchemy.orm import Session
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import UserORM, LessonORM, LearningPlanORM


def test_save_test_score(db: Session):
    # Setup: Create a user and a lesson
    user = UserORM(email="test_score@example.com", hashed_password="hash")
    db.add(user)
    db.flush()

    plan = LearningPlanORM(user_id=user.id, goal="Test Goal")
    db.add(plan)
    db.flush()

    lesson = LessonORM(
        plan_id=plan.id, order=1, title="Test Lesson", description="Test Description"
    )
    db.add(lesson)
    db.commit()

    repo = PlanRepository(db)

    # Action: Save a score
    score_val = 85
    saved_score = repo.save_test_score(user_id=user.id, lesson_id=lesson.id, score=score_val)

    # Assert
    assert saved_score.user_id == user.id
    assert saved_score.lesson_id == lesson.id
    assert saved_score.score == score_val
    assert saved_score.attempts == 1


def test_update_test_score(db: Session):
    # Setup: Create a user and a lesson
    user = UserORM(email="test_update@example.com", hashed_password="hash")
    db.add(user)
    db.flush()

    plan = LearningPlanORM(user_id=user.id, goal="Test Goal")
    db.add(plan)
    db.flush()

    lesson = LessonORM(
        plan_id=plan.id, order=1, title="Test Lesson", description="Test Description"
    )
    db.add(lesson)
    db.commit()

    repo = PlanRepository(db)

    # Action 1: Save first score
    repo.save_test_score(user_id=user.id, lesson_id=lesson.id, score=70)

    # Action 2: Update score
    updated_score = repo.save_test_score(user_id=user.id, lesson_id=lesson.id, score=90)

    # Assert
    assert updated_score.score == 90
    assert updated_score.attempts == 2
