# Practice Test Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement practice test submission, score calculation, and persistence to enable lesson completion based on test results.

**Architecture:** Add a new POST endpoint to submit test answers, calculate scores in the backend, and persist them via the PlanRepository. The frontend will subsequently trigger lesson completion via an existing PATCH endpoint.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic.

---

### Task 1: Define Submission Schemas

**Files:**
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Add TestSubmissionRequest, TestSubmissionResultItem, and TestSubmissionResponse schemas**

```python
class TestSubmissionRequest(BaseModel):
    answers: List[int]

class TestSubmissionResultItem(BaseModel):
    question_index: int
    is_correct: bool
    correct_answer_index: int
    explanation: str

class TestSubmissionResponse(BaseModel):
    score: int
    total: int
    results: List[TestSubmissionResultItem]
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/api/v1/schemas/recommendations.py
git commit -m "feat(api): add practice test submission schemas"
```

### Task 2: Update Repository for Score Persistence

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Add save_test_score method to PlanRepository**

```python
    def save_test_score(self, user_id: int, lesson_id: int, score: int) -> UserTestScoreORM:
        from datetime import datetime, timezone
        from sqlalchemy import select
        # Check if exists
        existing = self.db.scalar(
            select(UserTestScoreORM)
            .where(UserTestScoreORM.user_id == user_id)
            .where(UserTestScoreORM.lesson_id == lesson_id)
        )
        if existing:
            existing.score = score
            existing.attempts += 1
            existing.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            return existing
        
        new_score = UserTestScoreORM(
            user_id=user_id,
            lesson_id=lesson_id,
            score=score,
            attempts=1
        )
        self.db.add(new_score)
        self.db.commit()
        self.db.refresh(new_score)
        return new_score
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "feat(db): add save_test_score method to PlanRepository"
```

### Task 3: Implement Submission Endpoint

**Files:**
- Modify: `backend/app/api/v1/endpoints/lessons.py`
- Test: `backend/tests/test_practice_tests.py`

- [ ] **Step 1: Write failing integration test for submission**

In `backend/tests/test_practice_tests.py`, add:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_practice_tests.py -v`
Expected: FAIL (405 Method Not Allowed or 404)

- [ ] **Step 3: Implement the submit_lesson_test endpoint**

In `backend/app/api/v1/endpoints/lessons.py`:
```python
from app.api.v1.schemas.recommendations import (
    LessonDetail, 
    PracticeTestResponse, 
    TestSubmissionRequest, 
    TestSubmissionResponse,
    TestSubmissionResultItem
)

@router.post("/{lesson_id}/test/submit", response_model=TestSubmissionResponse)
async def submit_lesson_test(
    lesson_id: int,
    submission: TestSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")

    # 1. Get lesson and check ownership
    lesson = plan_repo.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    plan = plan_repo.get_by_id(current_user.id, lesson.plan_id)
    if not plan:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. Get the test
    test_orm = plan_repo.get_practice_test(lesson_id)
    if not test_orm:
        raise HTTPException(status_code=404, detail="No practice test found for this lesson")

    questions = test_orm.content["questions"]
    results = []
    correct_count = 0

    for i, q in enumerate(questions):
        submitted_idx = submission.answers[i] if i < len(submission.answers) else -1
        is_correct = submitted_idx == q["correct_answer_index"]
        if is_correct:
            correct_count += 1
        
        results.append(TestSubmissionResultItem(
            question_index=i,
            is_correct=is_correct,
            correct_answer_index=q["correct_answer_index"],
            explanation=q["explanation"]
        ))

    # 3. Save score
    plan_repo.save_test_score(current_user.id, lesson_id, correct_count)

    return TestSubmissionResponse(
        score=correct_count,
        total=len(questions),
        results=results
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest backend/tests/test_practice_tests.py -v`
Expected: PASS

- [ ] **Step 5: Add unauthorized and not found tests**

Add to `backend/tests/test_practice_tests.py`:
```python
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
```

- [ ] **Step 6: Final verification and commit**

Run: `pytest backend/tests/test_practice_tests.py -v`
Expected: ALL PASS

```bash
git add backend/app/api/v1/endpoints/lessons.py backend/tests/test_practice_tests.py
git commit -m "feat(api): implement practice test submission endpoint"
```
