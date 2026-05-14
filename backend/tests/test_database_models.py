from app.infrastructure.db.models import UserORM, UserSkillORM, UserTranscriptORM, LearningPlanORM


def test_user_orm_new_fields():
    user = UserORM(
        email="test@example.com",
        hashed_password="hash",
        career_goal="Become a Software Engineer",
        default_skill_level="Intermediate",
        default_learning_style="Theoretical",
        default_study_time=15,
    )
    assert user.email == "test@example.com"
    assert user.career_goal == "Become a Software Engineer"
    assert user.default_skill_level == "Intermediate"
    assert user.default_learning_style == "Theoretical"
    assert user.default_study_time == 15


def test_user_skill_orm():
    skill = UserSkillORM(user_id=1, skill_name="Python", mastery_level=3, category="Programming")
    assert skill.skill_name == "Python"
    assert skill.mastery_level == 3
    assert skill.category == "Programming"


def test_user_transcript_orm():
    entry = UserTranscriptORM(user_id=1, subject_name="CS101", credits=3.0, mark=4.0)
    assert entry.subject_name == "CS101"
    assert entry.credits == 3.0
    assert entry.mark == 4.0


def test_learning_plan_orm_new_fields():
    plan = LearningPlanORM(
        user_id=1,
        goal="Master ML",
        skill_level="Advanced",
        learning_style="Practical",
        study_time=20,
        interests=["frontend", "js"],
    )
    assert plan.skill_level == "Advanced"
    assert plan.learning_style == "Practical"
    assert plan.study_time == 20
    assert plan.interests == ["frontend", "js"]

from app.infrastructure.db.models import UserTestScoreORM

def test_user_test_score_orm():
    score = UserTestScoreORM(
        user_id=1,
        lesson_id=1,
        score=85,
        attempts=2,
        answers={"answers": [0, "python", True]}
    )
    assert score.user_id == 1
    assert score.lesson_id == 1
    assert score.score == 85
    assert score.attempts == 2
    assert score.answers == {"answers": [0, "python", True]}
