import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.db.models import CourseORM, CourseMaterialORM, LearningPlanORM, LessonORM, PracticeTestORM, UserTestScoreORM
from app.infrastructure.ai.analysis_agent import GlobalAnalysis
from app.domain.recommendation.entities import Lesson, SkillGapAnalysis, LearningMaterial

@pytest.fixture
def mock_courses(db: Session):
    course = CourseORM(
        subject_name="Test Course",
        description="Test Course Description",
        skills_taught={"test_skill": 5}
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    material = CourseMaterialORM(
        course_id=course.id,
        filename="test_material.txt",
        content="This is the content of the test material.",
        status="analyzed"
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return course, material

@patch("app.services.advisor_service.generate_global_analysis")
def test_generate_plan_copies_content(mock_gen, client: TestClient, admin_token_headers, db: Session, mock_courses):
    course, material = mock_courses
    
    # Mock AI response
    mock_gen.return_value = GlobalAnalysis(
        skill_gap_analysis=SkillGapAnalysis(overall_gap_score=0.5, domain_breakdown=[], critical_skills=[]),
        learning_path=[
            Lesson(
                order=1,
                title="Introduction to Test",
                description="Learning test basics",
                resource_id=str(material.id),
                is_external=False,
                status="current",
                materials=[LearningMaterial(title="Extra", description="Extra help", url="http://example.com", type="video")]
            )
        ]
    )
    
    response = client.post("/api/v1/learning-plan/generate", 
        json={
            "goal": "Test Lesson Isolation",
            "skill_level": "Beginner",
            "learning_style": "Practical",
            "study_time": 10,
            "interests": ["testing"]
        },
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    plan_data = response.json()
    plan_id = plan_data["id"]
    
    # Verify content was copied
    step_order = plan_data["steps"][0]["order"]
    response = client.get(f"/api/v1/learning-plan/{plan_id}/steps/{step_order}", headers=admin_token_headers)
    assert response.status_code == 200
    lesson_detail = response.json()
    assert lesson_detail["content"] == material.content

@patch("app.services.advisor_service.generate_global_analysis")
@patch("app.api.v1.endpoints.learning_plan.get_arq_pool")
def test_lesson_isolation_and_tests(mock_arq, mock_gen, client: TestClient, admin_token_headers, db: Session, mock_courses):
    course, material = mock_courses
    mock_arq.return_value = MagicMock()
    
    # Mock AI response with 2 steps
    mock_gen.return_value = GlobalAnalysis(
        skill_gap_analysis=SkillGapAnalysis(overall_gap_score=0.5, domain_breakdown=[], critical_skills=[]),
        learning_path=[
            Lesson(
                order=1,
                title="Lesson 1",
                description="First lesson",
                resource_id=str(material.id),
                is_external=False,
                status="current",
                materials=[]
            ),
            Lesson(
                order=2,
                title="Lesson 2",
                description="Second lesson",
                resource_id=str(material.id),
                is_external=False,
                status="upcoming",
                materials=[]
            )
        ]
    )
    
    # 1. Generate Plan A
    response = client.post("/api/v1/learning-plan/generate", 
        json={"goal": "Plan A", "skill_level": "Beginner", "learning_style": "Practical", "study_time": 10, "interests": []},
        headers=admin_token_headers
    )
    plan_a_id = response.json()["id"]
    
    # 2. Generate Plan B (Plan A will be deactivated, but still exists)
    response = client.post("/api/v1/learning-plan/generate", 
        json={"goal": "Plan B", "skill_level": "Beginner", "learning_style": "Practical", "study_time": 10, "interests": []},
        headers=admin_token_headers
    )
    plan_b_id = response.json()["id"]
    
    # Get lesson IDs from Plan A and Plan B
    lessons_a = db.execute(select(LessonORM).where(LessonORM.plan_id == plan_a_id).order_by(LessonORM.order)).scalars().all()
    lessons_b = db.execute(select(LessonORM).where(LessonORM.plan_id == plan_b_id).order_by(LessonORM.order)).scalars().all()
    
    assert len(lessons_a) == 2
    assert len(lessons_b) == 2
    assert lessons_a[0].id != lessons_b[0].id
    
    # 3. Create a practice test for Lesson A1
    test_a1 = PracticeTestORM(lesson_id=lessons_a[0].id, content={"questions": []})
    db.add(test_a1)
    db.commit()
    
    # 4. Verify GET /test for A1 returns test, but B1 returns 404 (if not generated)
    response = client.get(f"/api/v1/learning-plan/{plan_a_id}/steps/1/test", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_a1.id
    
    response = client.get(f"/api/v1/learning-plan/{plan_b_id}/steps/1/test", headers=admin_token_headers)
    assert response.status_code == 404 # Not generated yet
    
    # 5. Submit test for A1
    response = client.post(f"/api/v1/learning-plan/{plan_a_id}/steps/1/test/submit", json={"score": 85}, headers=admin_token_headers)
    assert response.status_code == 200
    
    # 6. Verify isolation: Plan A Step 1 is completed, Step 2 is current. Plan B Step 1 is still current.
    # Plan A
    plan_a_detail = client.get(f"/api/v1/learning-plan/{plan_a_id}", headers=admin_token_headers).json()
    assert plan_a_detail["steps"][0]["status"] == "completed"
    assert plan_a_detail["steps"][0]["score"] == 85
    assert plan_a_detail["steps"][1]["status"] == "current"
    
    # Plan B
    plan_b_detail = client.get(f"/api/v1/learning-plan/{plan_b_id}", headers=admin_token_headers).json()
    assert plan_b_detail["steps"][0]["status"] == "current"
    assert plan_b_detail["steps"][0]["score"] is None
    assert plan_b_detail["steps"][1]["status"] == "upcoming"


@patch("app.services.advisor_service.generate_global_analysis")
def test_generate_plan_copies_previous_scores(mock_gen, client: TestClient, admin_token_headers, db: Session, mock_courses):
    course, material = mock_courses
    
    # 1. Generate Plan A with one lesson
    mock_gen.return_value = GlobalAnalysis(
        skill_gap_analysis=SkillGapAnalysis(overall_gap_score=0.5, domain_breakdown=[], critical_skills=[]),
        learning_path=[
            Lesson(
                order=1, title="Lesson 1", description="D", resource_id=str(material.id),
                is_external=False, status="current", materials=[]
            )
        ]
    )
    
    response = client.post("/api/v1/learning-plan/generate", 
        json={"goal": "Plan A", "skill_level": "Beginner", "learning_style": "Practical", "study_time": 10, "interests": []},
        headers=admin_token_headers
    )
    plan_a_id = response.json()["id"]
    lesson_a1_id = db.execute(select(LessonORM.id).where(LessonORM.plan_id == plan_a_id)).scalar()
    
    # 2. Submit a high score for Plan A Lesson 1
    client.post(f"/api/v1/learning-plan/{plan_a_id}/steps/1/test/submit", json={"score": 90}, headers=admin_token_headers)
    
    # 3. Generate Plan B with the SAME material
    mock_gen.return_value = GlobalAnalysis(
        skill_gap_analysis=SkillGapAnalysis(overall_gap_score=0.5, domain_breakdown=[], critical_skills=[]),
        learning_path=[
            Lesson(
                order=1, title="Lesson 1 Again", description="D", resource_id=str(material.id),
                is_external=False, status="upcoming", materials=[]
            )
        ]
    )
    
    response = client.post("/api/v1/learning-plan/generate", 
        json={"goal": "Plan B", "skill_level": "Beginner", "learning_style": "Practical", "study_time": 10, "interests": []},
        headers=admin_token_headers
    )
    plan_b_id = response.json()["id"]
    
    # 4. Verify Plan B Lesson 1 is automatically COMPLETED and has the score COPIED
    plan_b_detail = client.get(f"/api/v1/learning-plan/{plan_b_id}", headers=admin_token_headers).json()
    assert plan_b_detail["steps"][0]["status"] == "completed"
    assert plan_b_detail["steps"][0]["score"] == 90
