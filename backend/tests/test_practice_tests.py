import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.infrastructure.db.models import LearningPlanORM, LessonORM, UserORM
from app.core.security import get_password_hash


@pytest.fixture
def seeded_lesson(db, normal_user):
    plan = LearningPlanORM(user_id=normal_user.id, goal="Learn Python", is_active=True)
    db.add(plan)
    db.flush()

    lesson = LessonORM(
        plan_id=plan.id,
        order=1,
        title="Python Basics",
        description="Introduction to Python",
        content="Python is a programming language.",
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
        full_name="Other User",
    )
    db.add(other_user)
    db.flush()

    plan = LearningPlanORM(user_id=other_user.id, goal="Learn Java", is_active=True)
    db.add(plan)
    db.flush()

    lesson = LessonORM(
        plan_id=plan.id, order=1, title="Java Basics", description="Introduction to Java"
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def test_get_practice_test_success(client: TestClient, normal_user_token_headers, seeded_lesson):
    # Mock LLM
    mock_response = AsyncMock()
    mock_response.text = '[{"type": "multiple_choice", "question": "What is Python?", "options": ["A snake", "A language", "Both", "None"], "correct_answer_index": 2, "explanation": "It is both."}]'

    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_response.text))]
        )
        mock_openai.return_value = mock_client

        response = client.get(
            f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question"] == "What is Python?"


def test_get_practice_test_persistence(
    client: TestClient, normal_user_token_headers, seeded_lesson
):
    # Mock LLM
    mock_response = AsyncMock()
    mock_response.text = '[{"type": "multiple_choice", "question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'

    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_response.text))]
        )
        mock_openai.return_value = mock_client

        # First call
        response1 = client.get(
            f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers
        )
        assert response1.status_code == 200

        # Second call
        response2 = client.get(
            f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers
        )
        assert response2.status_code == 200
        assert response1.json() == response2.json()

        # Ensure LLM called only once
        if mock_llama_openai and mock_llama_openai.called:
             assert mock_llm.acomplete.call_count == 1
        else:
             assert mock_client.chat.completions.create.call_count == 1


def test_get_practice_test_unauthorized(
    client: TestClient, normal_user_token_headers, other_user_lesson
):
    response = client.get(
        f"/api/v1/learning-plan/{other_user_lesson.plan_id}/lessons/{other_user_lesson.order}/test", headers=normal_user_token_headers
    )
    assert response.status_code == 403


def test_get_practice_test_not_found(client: TestClient, normal_user_token_headers):
    response = client.get("/api/v1/learning-plan/9999/lessons/1/test", headers=normal_user_token_headers)
    assert response.status_code == 404


def test_submit_practice_test_success(
    client: TestClient, normal_user_token_headers, seeded_lesson, db
):
    # First generate a test
    mock_response = AsyncMock()
    mock_response.text = '[{"type": "multiple_choice", "question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'
    
    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_response.text))]
        )
        mock_openai.return_value = mock_client
        
        client.get(f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers)

    # Submit answers
    response = client.post(
        f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 1
    assert data["total"] == 1
    assert data["results"][0]["is_correct"] is True


def test_submit_practice_test_mixed_types(
    client: TestClient, normal_user_token_headers, seeded_lesson, db
):
    # First generate a test with mixed types
    mock_response = AsyncMock()
    mock_json = """
    [
        {"type": "multiple_choice", "question": "MCQ", "options": ["O0", "O1", "O2", "O3"], "correct_answer_index": 1, "explanation": "E1"},
        {"type": "short_answer", "question": "SAQ", "correct_answer_text": "Python", "explanation": "E2"},
        {"type": "true_false", "question": "true_false", "options": ["True", "False"], "correct_answer_index": 0, "explanation": "E3"},
        {"type": "fill_in_the_blank", "question": "FIB ____", "correct_answer_text": "is great", "explanation": "E4"}
    ]
    """
    mock_response.text = mock_json

    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_json))]
        )
        mock_openai.return_value = mock_client

        response = client.get(f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers)
        assert response.status_code == 200

    # Submit answers
    response = client.post(
        f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [1, "python ", 0, "IS GREAT"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 4
    assert data["total"] == 4
    for i in range(4):
        assert data["results"][i]["is_correct"] is True


def test_submit_practice_test_unauthorized(
    client: TestClient, normal_user_token_headers, other_user_lesson
):
    response = client.post(
        f"/api/v1/learning-plan/{other_user_lesson.plan_id}/lessons/{other_user_lesson.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]},
    )
    assert response.status_code == 403


def test_submit_practice_test_no_test(client: TestClient, normal_user_token_headers, seeded_lesson):
    response = client.post(
        f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]},
    )
    assert response.status_code == 404


def test_submit_test_unlocks_next_lesson_and_saves_percentage(
    client: TestClient, normal_user_token_headers, db, normal_user
):
    # Setup: Plan with two lessons
    plan = LearningPlanORM(user_id=normal_user.id, goal="Test Plan", is_active=True)
    db.add(plan)
    db.flush()
    l1 = LessonORM(plan_id=plan.id, order=1, title="L1", description="D1", status="current")
    l2 = LessonORM(plan_id=plan.id, order=2, title="L2", description="D2", status="upcoming")
    db.add(l1)
    db.add(l2)
    db.commit()

    # 1. Generate test for L1
    mock_response = AsyncMock()
    mock_response.text = '[{"type": "multiple_choice", "question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'
    
    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai, \
         patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_response.text))]
        )
        mock_openai.return_value = mock_client
        
        client.get(f"/api/v1/learning-plan/{plan.id}/lessons/{l1.order}/test", headers=normal_user_token_headers)

    # 2. Submit test
    response = client.post(
        f"/api/v1/learning-plan/{plan.id}/lessons/{l1.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]},
    )
    assert response.status_code == 200

    # 3. Verify L1 completed, L2 current, and score is 100
    response = client.get(f"/api/v1/learning-plan/{plan.id}", headers=normal_user_token_headers)
    data = response.json()
    steps = {s["id"]: s for s in data["steps"]}

    assert steps[l1.id]["status"] == "completed"
    assert steps[l1.id]["score"] == 100
    assert steps[l2.id]["status"] == "current"

def test_practice_test_review_persistence(
    client: TestClient, normal_user_token_headers, seeded_lesson, db
):
    # 1. Generate a test
    mock_response = AsyncMock()
    mock_response.text = '[{"type": "multiple_choice", "question": "Q1", "options": ["O1", "O2", "O3", "O4"], "correct_answer_index": 0, "explanation": "E1"}]'
    
    with patch("app.services.lesson_service.LlamaOpenAI") as mock_llama_openai,          patch("openai.AsyncOpenAI") as mock_openai:
        
        mock_llm = AsyncMock()
        mock_llm.acomplete.return_value = mock_response
        if mock_llama_openai:
            mock_llama_openai.return_value = mock_llm

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(content=mock_response.text))]
        )
        mock_openai.return_value = mock_client
        
        client.get(f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test", headers=normal_user_token_headers)

    # 2. Submit answers
    submit_response = client.post(
        f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test/submit",
        headers=normal_user_token_headers,
        json={"answers": [0]},
    )
    assert submit_response.status_code == 200
    submit_data = submit_response.json()
    assert submit_data["results"][0]["user_answer"] == 0

    # 3. Retrieve the test again and verify last_attempt is populated
    response = client.get(
        f"/api/v1/learning-plan/{seeded_lesson.plan_id}/lessons/{seeded_lesson.order}/test",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["last_attempt"] is not None
    assert data["last_attempt"]["score"] == 1
    assert data["last_attempt"]["total"] == 1
    assert data["last_attempt"]["results"][0]["user_answer"] == 0
    assert data["last_attempt"]["results"][0]["explanation"] == "E1"
