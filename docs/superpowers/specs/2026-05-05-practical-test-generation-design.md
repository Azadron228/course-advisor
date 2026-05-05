# Design Spec: Practical Test Generation

## Overview
Add a new API endpoint to automatically generate 5-question multiple-choice practice tests for lessons using AI. Tests are generated on-the-fly if they don't exist and are persisted in the database.

## User Experience
*   When a user views a lesson, they can request a practice test.
*   The system provides 5 multiple-choice questions based on the lesson content.
*   Mathematical expressions are rendered using KaTeX/LaTeX syntax.

## Technical Design

### 1. Data Structures (`app/api/v1/schemas/recommendations.py`)
```python
class Question(BaseModel):
    text: str
    options: List[str]
    correct_answer_index: int

class PracticeTestResponse(BaseModel):
    id: int
    lesson_id: int
    questions: List[Question]
```

### 2. Database Layer (`app/infrastructure/db/models.py`)
Uses the existing `PracticeTestORM`:
*   `id`: Primary key.
*   `lesson_id`: Foreign key to `lessons.id`.
*   `content`: JSON field storing the list of questions.

### 3. Repository Layer (`app/infrastructure/db/repositories/plan_repository.py`)
Add methods:
*   `get_practice_test(lesson_id: int) -> Optional[PracticeTestORM]`
*   `create_practice_test(lesson_id: int, content: dict) -> PracticeTestORM`

### 4. API Endpoint (`app/api/v1/endpoints/lessons.py`)
*   `GET /lessons/{lesson_id}/test`
*   **Logic**:
    1. Validate user ownership of the lesson via its `plan_id`.
    2. Check `PracticeTestORM` for existing test for `lesson_id`.
    3. If not found:
        *   Prompt LLM (GPT-4o) to generate 5 multiple-choice questions.
        *   **Prompt Requirements**:
            *   Based on lesson `title`, `description`, and `content`.
            *   Strict JSON output.
            *   LaTeX for math (Inline: `$`, Block: `$$`).
        *   Save to database.
    4. Return the test content.

## Verification Plan
### Automated Tests
*   `tests/test_practice_tests.py`:
    *   Test successful generation and retrieval.
    *   Test unauthorized access (trying to get a test for a lesson from another user's plan).
    *   Test persistence (subsequent calls return the same test).
