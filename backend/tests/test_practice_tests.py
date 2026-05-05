import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.infrastructure.db.models import LearningPlanORM, LessonORM, UserORM
from app.core.security import get_password_hash

@pytest.fixture
def seeded_lesson(db, normal_user):
    plan = LearningPlanORM(
        user_id=normal_user.id,
        goal="Learn Python",
        is_active=True
    )
    db.add(plan)
    db.flush()
    
    lesson = LessonORM(
        plan_id=plan.id,
        order=1,
        title="Python Basics",
        description="Introduction to Python",
        content="Python is a programming language."
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

@pytest.fixture
def other_user_lesson(db):
    other_user = UserORM(
        email="other@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Other User"
    )
    db.add(other_user)
    db.flush()
    
    plan = LearningPlanORM(
        user_id=other_user.id,
        goal="Learn Java",
        is_active=True
    )
    db.add(plan)
    db.flush()
    
    lesson = LessonORM(
        plan_id=plan.id,
        order=1,
        title="Java Basics",
        description="Introduction to Java"
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

def test_get_practice_test_success(client: TestClient, normal_user_token_headers, seeded_lesson):
    # Mock LLM
    mock_response = AsyncMock()
    mock_response.text = '[{"question": "What is Python?", "options": ["A snake", "A language", "Both", "None"], "correct_answer_index": 2, "explanation": "It is both."}]'
    
    with patch("app.api.v1.endpoints.lessons.OpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        response = client.get(
            f"/api/v1/lessons/{seeded_lesson.id}/test",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question"] == "What is Python?"

def test_get_practice_test_persistence(client: TestClient, normal_user_token_headers, seeded_lesson):
    # Mock LLM
    mock_response = AsyncMock()
    mock_response.text = '[{"question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'
    
    with patch("app.api.v1.endpoints.lessons.OpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        # First call
        response1 = client.get(
            f"/api/v1/lessons/{seeded_lesson.id}/test",
            headers=normal_user_token_headers
        )
        assert response1.status_code == 200
        
        # Second call
        response2 = client.get(
            f"/api/v1/lessons/{seeded_lesson.id}/test",
            headers=normal_user_token_headers
        )
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        
        # Ensure LLM called only once
        assert mock_llm.acomplete.call_count == 1

def test_get_practice_test_unauthorized(client: TestClient, normal_user_token_headers, other_user_lesson):
    response = client.get(
        f"/api/v1/lessons/{other_user_lesson.id}/test",
        headers=normal_user_token_headers
    )
    assert response.status_code == 403

def test_get_practice_test_not_found(client: TestClient, normal_user_token_headers):
    response = client.get(
        "/api/v1/lessons/9999/test",
        headers=normal_user_token_headers
    )
    assert response.status_code == 404

def test_submit_practice_test_success(client: TestClient, normal_user_token_headers, seeded_lesson, db):
    # First generate a test
    mock_response = AsyncMock()
    mock_response.text = '[{"question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'
    with patch("app.api.v1.endpoints.lessons.OpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        mock_openai.return_value = mock_llm
        client.get(f"/api/v1/lessons/{seeded_lesson.id}/test", headers=normal_user_token_headers)

    # Submit answers
    response = client.post(
        f"/api/v1/lessons/{seeded_lesson.id}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 1
    assert data["total"] == 1
    assert data["results"][0]["is_correct"] is True

def test_submit_practice_test_unauthorized(client: TestClient, normal_user_token_headers, other_user_lesson):
    response = client.post(
        f"/api/v1/lessons/{other_user_lesson.id}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]}
    )
    assert response.status_code == 403

def test_submit_practice_test_no_test(client: TestClient, normal_user_token_headers, seeded_lesson):
    response = client.post(
        f"/api/v1/lessons/{seeded_lesson.id}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]}
    )
    assert response.status_code == 404
