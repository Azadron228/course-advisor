# Design Spec: Practice Test Answer Viewing

Allow users to view their submitted answers for practice tests, both immediately after completion and when revisiting a lesson.

## Goals
- Persist user answers in the database.
- Provide a detailed review view in the frontend.
- Show user's answer, correct answer, and explanation for each question.

## Architecture

### Database
- **Table:** `user_test_scores`
- **New Column:** `answers` (JSON, nullable=False)
- **Migration:** New Alembic migration to add the column.

### Backend

#### Schemas (`backend/app/api/v1/schemas/recommendations.py`)
- `TestSubmissionResultItem`: Add `user_answer: Union[int, str, bool]`.
- `PracticeTestResponse`: Add `last_attempt: Optional[TestSubmissionResponse]`.

#### Repository (`backend/app/infrastructure/db/repositories/plan_repository.py`)
- Update `save_test_score` to accept `answers`.
- Add `get_last_test_score(user_id, lesson_id)` to retrieve previous attempts.

#### Service (`backend/app/services/lesson_service.py`)
- `submit_practice_test`: 
    - Save `answers` to DB.
    - Include `user_answer` in `TestSubmissionResultItem`.
- `get_practice_test`: 
    - Fetch previous score and answers from DB.
    - Include them in `PracticeTestResponse`.

### Frontend

#### UI Component (`frontend/src/components/features/practice-test-ui.tsx`)
- Add `viewMode` state: `'test' | 'summary' | 'review'`.
- `ResultsSummary`: Add "Review Answers" button.
- `ReviewDetails`: New view showing all questions in a list with detailed feedback.
- If `testData.last_attempt` is present, show the `ResultsSummary` (or `ReviewDetails`) immediately instead of the test.

## Success Criteria
- User can see their specific answers after submitting.
- User can see their previous answers when returning to a completed lesson.
- Correct answers and explanations are clearly visible for each question in review mode.
