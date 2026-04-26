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
