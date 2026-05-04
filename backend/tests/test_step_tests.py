from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.infrastructure.db.models import LearningPlanORM, LessonORM, PracticeTestORM, CourseMaterialORM

def test_step_test_endpoints(client: TestClient, db: Session, admin_token_headers):
    # 1. Setup data
    course = CourseMaterialORM(course_id=1, filename="test.pdf", content="Some content")
    db.add(course)
    db.flush()

    plan = LearningPlanORM(user_id=1, goal="Test Goal")
    db.add(plan)
    db.flush()

    lesson = LessonORM(
        plan_id=plan.id,
        order=1,
        title="Lesson 1",
        description="Desc",
        material_id=course.id,
        status="current"
    )
    db.add(lesson)
    db.flush()

    practice_test = PracticeTestORM(
        lesson_id=lesson.id,
        content={"questions": [{"question": "What is 1+1?", "options": ["1", "2"], "answer": "2"}]}
    )
    db.add(practice_test)
    db.commit()

    # 2. Test GET /steps/{step_order}/test
    r = client.get(f"/api/v1/learning-plan/{plan.id}/steps/1/test", headers=admin_token_headers)
    assert r.status_code == 200
    assert r.json()["lesson_id"] == lesson.id

    # 3. Test POST /steps/{step_order}/test/submit
    r = client.post(
        f"/api/v1/learning-plan/{plan.id}/steps/1/test/submit",
        json={"score": 80},
        headers=admin_token_headers
    )
    assert r.status_code == 200
    assert r.json()["message"] == "Score saved successfully"

    # 4. Verify lesson status and score
    db.refresh(lesson)
    assert lesson.status == "completed"

    r = client.get(f"/api/v1/learning-plan/{plan.id}/steps/1", headers=admin_token_headers)
    assert r.status_code == 200
    assert r.json()["score"] == 80
