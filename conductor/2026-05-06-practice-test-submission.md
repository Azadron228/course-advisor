# Practice Test Submission Plan

## Objective
Add functionality to proceed to the next lesson after completing a practice test, adhering to the "Two-Step Frontend-Driven" approach.

## Key Files & Context
- `backend/app/api/v1/schemas/recommendations.py`: Add schemas for test submission request and response.
- `backend/app/infrastructure/db/repositories/plan_repository.py`: Add method to save the test score.
- `backend/app/api/v1/endpoints/lessons.py`: Add `POST /api/v1/lessons/{lesson_id}/test/submit` endpoint.
- `backend/tests/test_practice_tests.py`: Add tests for the new endpoint.

## Implementation Steps

### 1. Schemas (`app/api/v1/schemas/recommendations.py`)
Add the following classes:
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

### 2. Repository (`app/infrastructure/db/repositories/plan_repository.py`)
Add method `save_test_score`:
```python
def save_test_score(self, user_id: int, lesson_id: int, score: int) -> UserTestScoreORM:
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

### 3. API Endpoint (`app/api/v1/endpoints/lessons.py`)
Add `POST /api/v1/lessons/{lesson_id}/test/submit`:
- Validate user and lesson ownership.
- Fetch `PracticeTestORM`. If missing, 404.
- Compare submitted `answers` against `test_orm.content["questions"]`.
- Calculate `score` (percentage 0-100 or raw correct count. Let's use raw correct count based on the schema returning `total`).
- Call `plan_repo.save_test_score(current_user.id, lesson_id, score)`.
- Return `TestSubmissionResponse`.
- (The client will subsequently call `PATCH /api/v1/lessons/{lesson_id}` with `status="completed"` to unlock the next lesson).

### 4. Verification & Testing (`backend/tests/test_practice_tests.py`)
Add tests:
- `test_submit_practice_test_success`: Submit correct answers, get 100% score, check DB.
- `test_submit_practice_test_incorrect`: Submit wrong answers, get 0% score.
- `test_submit_practice_test_unauthorized`: Submit to someone else's lesson (403).
- `test_submit_practice_test_not_found`: Submit to lesson with no test (404).

## Migration & Rollback
- No database migrations needed as models exist. Rollback is just reversing the code changes.
