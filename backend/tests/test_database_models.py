from app.infrastructure.db.models import UserORM, UserSkillORM, UserTranscriptORM, LearningPlanORM, CourseORM, CourseMaterialORM
from datetime import datetime

def test_course_orm_instantiation():
    course = CourseORM(
        subject_name="AI 101",
        description="Intro to AI",
        skills_taught=["AI", "Python"],
    )
    assert course.subject_name == "AI 101"
    assert course.skills_taught == ["AI", "Python"]

def test_course_material_orm_instantiation():
    material = CourseMaterialORM(
        course_id=1,
        filename="test.pdf",
        content="some content",
        status="analyzed",
        created_at=datetime.utcnow()
    )
    assert material.filename == "test.pdf"
    assert material.status == "analyzed"

def test_user_orm_new_fields():
    user = UserORM(
        email="test@example.com",
        hashed_password="hash",
        career_goal="Become a Software Engineer",
        default_skill_level="Intermediate",
        default_learning_style="Theoretical",
        default_study_time=15
    )
    assert user.email == "test@example.com"
    assert user.career_goal == "Become a Software Engineer"
    assert user.default_skill_level == "Intermediate"
    assert user.default_learning_style == "Theoretical"
    assert user.default_study_time == 15

def test_user_skill_orm():
    skill = UserSkillORM(
        user_id=1,
        skill_name="Python",
        mastery_level=3,
        category="Programming"
    )
    assert skill.skill_name == "Python"
    assert skill.mastery_level == 3
    assert skill.category == "Programming"

def test_user_transcript_orm():
    entry = UserTranscriptORM(
        user_id=1,
        subject_name="CS101",
        credits=3.0,
        mark=4.0
    )
    assert entry.subject_name == "CS101"
    assert entry.credits == 3.0
    assert entry.mark == 4.0

def test_learning_plan_orm_new_fields():
    plan = LearningPlanORM(
        user_id=1,
        goal="Master ML",
        steps={"nodes": []},
        skill_level="Advanced",
        learning_style="Practical",
        study_time=20,
        interests=["frontend", "js"]
    )
    assert plan.skill_level == "Advanced"
    assert plan.learning_style == "Practical"
    assert plan.study_time == 20
    assert plan.interests == ["frontend", "js"]
