from app.infrastructure.db.models import UserORM, UserSkillORM, UserTranscriptORM, LearningPlanORM

def test_user_orm_new_fields():
    user = UserORM(
        email="test@example.com",
        hashed_password="hash",
        career_goal="Become a Software Engineer",
        onboarding_completed=True
    )
    assert user.career_goal == "Become a Software Engineer"
    assert user.onboarding_completed is True

def test_user_skill_orm_instantiation():
    skill = UserSkillORM(
        user_id=1,
        skill_name="Python",
        mastery_level=50,
        category="Programming"
    )
    assert skill.skill_name == "Python"
    assert skill.mastery_level == 50

def test_user_transcript_orm_instantiation():
    transcript = UserTranscriptORM(
        user_id=1,
        subject_name="CS101",
        credits=3.0,
        mark=85.0
    )
    assert transcript.subject_name == "CS101"

def test_learning_plan_orm_instantiation():
    plan = LearningPlanORM(
        user_id=1,
        goal="Learn AI",
        steps=[{"step": 1, "desc": "Study Math"}],
        is_active=True
    )
    assert plan.goal == "Learn AI"

def test_user_orm_advanced_fields():
    user = UserORM(
        email="adv@example.com",
        hashed_password="hash",
        default_skill_level="Intermediate",
        default_learning_style="Visual",
        default_study_time=15
    )
    assert user.default_skill_level == "Intermediate"
    assert user.default_learning_style == "Visual"
    assert user.default_study_time == 15

def test_learning_plan_orm_advanced_fields():
    plan = LearningPlanORM(
        user_id=1,
        goal="Learn React",
        steps=[],
        skill_level="Advanced",
        learning_style="Practical",
        study_time=20,
        interests=["frontend", "js"]
    )
    assert plan.skill_level == "Advanced"
    assert plan.learning_style == "Practical"
    assert plan.study_time == 20
    assert plan.interests == ["frontend", "js"]
