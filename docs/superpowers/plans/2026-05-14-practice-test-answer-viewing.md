# Practice Test Answer Viewing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to persist and view their submitted answers for practice tests.

**Architecture:** 
1. Add `answers` column to `user_test_scores` table.
2. Update backend schemas and services to save and retrieve answers.
3. Refactor frontend `PracticeTestUI` to include a Review mode.

**Tech Stack:** Python (FastAPI, SQLAlchemy, Alembic), TypeScript (Next.js, Tailwind CSS, Lucide React).

---

### Task 1: Database Migration

**Files:**
- Create: `backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py`
- Modify: `backend/app/infrastructure/db/models.py:120-132`

- [ ] **Step 1: Update the UserTestScoreORM model**
Add `answers: Mapped[dict] = mapped_column(JSON, nullable=True)` to `UserTestScoreORM`.

```python
# backend/app/infrastructure/db/models.py
class UserTestScoreORM(Base):
    __tablename__ = "user_test_scores"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    answers: Mapped[dict] = mapped_column(JSON, nullable=True)  # Store user's submitted answers
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
```

- [ ] **Step 2: Create the Alembic migration**
Create a new file `backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py`.

```python
"""add answers to test scores

Revision ID: a7f8e9c1d2b3
Revises: fff1a80f1966
Create Date: 2026-05-14 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a7f8e9c1d2b3'
down_revision: Union[str, Sequence[str], None] = 'fff1a80f1966'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('user_test_scores', sa.Column('answers', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('user_test_scores', 'answers')
```

- [ ] **Step 3: Run migration**
Run: `cd backend && alembic upgrade head`
Expected: Successfully upgraded to `a7f8e9c1d2b3`.

- [ ] **Step 4: Commit**
```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py
git commit -m "db: add answers column to user_test_scores"
```

### Task 2: Backend Schema Updates

**Files:**
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Update TestSubmissionResultItem and TestSubmissionResponse**
Add `user_answer` to `TestSubmissionResultItem`.

```python
# backend/app/api/v1/schemas/recommendations.py
class TestSubmissionResultItem(BaseModel):
    question_index: int
    is_correct: bool
    user_answer: Optional[Union[int, str, bool]] = None # New field
    correct_answer_index: Optional[int] = None
    correct_answer_text: Optional[str] = None
    explanation: str

class TestSubmissionResponse(BaseModel):
    score: int
    total: int
    results: List[TestSubmissionResultItem]
```

- [ ] **Step 2: Update PracticeTestResponse**
Add `last_attempt` to `PracticeTestResponse`.

```python
# backend/app/api/v1/schemas/recommendations.py
class PracticeTestResponse(BaseModel):
    id: int
    lesson_id: int
    questions: List[Question]
    last_attempt: Optional[TestSubmissionResponse] = None # New field
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 3: Commit**
```bash
git add backend/app/api/v1/schemas/recommendations.py
git commit -m "schema: update practice test schemas to include user answers and last attempt"
```

### Task 3: Repository and Service Updates

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`
- Modify: `backend/app/services/lesson_service.py`

- [ ] **Step 1: Update PlanRepository**
Update `save_test_score` to accept `answers` and add `get_last_test_score`.

```python
# backend/app/infrastructure/db/repositories/plan_repository.py

    def save_test_score(self, user_id: int, lesson_id: int, score: int, answers: list) -> None:
        existing = self.db.query(UserTestScoreORM).filter_by(
            user_id=user_id, lesson_id=lesson_id
        ).first()
        if existing:
            existing.score = score
            existing.answers = {"answers": answers}
            existing.attempts += 1
            existing.completed_at = datetime.now(timezone.utc)
        else:
            new_score = UserTestScoreORM(
                user_id=user_id,
                lesson_id=lesson_id,
                score=score,
                answers={"answers": answers}
            )
            self.db.add(new_score)
        self.db.commit()

    def get_last_test_score(self, user_id: int, lesson_id: int) -> Optional[UserTestScoreORM]:
        return self.db.query(UserTestScoreORM).filter_by(
            user_id=user_id, lesson_id=lesson_id
        ).first()
```

- [ ] **Step 2: Update submit_practice_test in LessonService**
Populate `user_answer` and pass `submission.answers` to repository.

```python
# backend/app/services/lesson_service.py:230-280
    async def submit_practice_test(
        self, user: User, lesson_id: int, submission: TestSubmissionRequest
    ) -> Optional[TestSubmissionResponse]:
        # ... (rest of logic before loop)
        for i, q in enumerate(questions):
            submitted = submission.answers[i] if i < len(submission.answers) else None
            # ... (is_correct calculation)
            results.append(
                TestSubmissionResultItem(
                    question_index=i,
                    is_correct=is_correct,
                    user_answer=submitted, # New
                    correct_answer_index=q.get("correct_answer_index"),
                    correct_answer_text=q.get("correct_answer_text"),
                    explanation=q["explanation"],
                )
            )

        # 3. Save score as percentage and answers
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user.id, lesson_id, score_percentage, submission.answers)
        # ...
```

- [ ] **Step 3: Update get_practice_test and extract is_correct logic in LessonService**
Extract the question grading logic to a private method `_grade_question` and use it in both `submit_practice_test` and `get_practice_test`.

```python
# backend/app/services/lesson_service.py

    def _grade_question(self, question: dict, submitted: Any) -> bool:
        q_type = question.get("type", "multiple_choice")
        if q_type in ["multiple_choice", "true_false"]:
            return submitted == question.get("correct_answer_index")
        elif q_type in ["short_answer", "fill_in_the_blank"]:
            if isinstance(submitted, str) and question.get("correct_answer_text"):
                return submitted.strip().lower() == question["correct_answer_text"].strip().lower()
        return False

    async def get_practice_test(self, user: User, lesson_id: int) -> Optional[PracticeTestResponse]:
        # ... (lesson/plan checks)
        
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        # ... (generation logic)

        last_score = self.plan_repo.get_last_test_score(user.id, lesson_id)
        last_attempt = None
        if last_score and last_score.answers:
            questions = test_orm.content["questions"]
            prev_answers = last_score.answers.get("answers", [])
            results = []
            for i, q in enumerate(questions):
                submitted = prev_answers[i] if i < len(prev_answers) else None
                is_correct = self._grade_question(q, submitted)
                results.append(
                    TestSubmissionResultItem(
                        question_index=i,
                        is_correct=is_correct,
                        user_answer=submitted,
                        correct_answer_index=q.get("correct_answer_index"),
                        correct_answer_text=q.get("correct_answer_text"),
                        explanation=q["explanation"],
                    )
                )
            
            last_attempt = TestSubmissionResponse(
                score=int((last_score.score / 100) * len(questions)),
                total=len(questions),
                results=results
            )

        return PracticeTestResponse(
            id=test_orm.id,
            lesson_id=test_orm.lesson_id,
            questions=test_orm.content["questions"],
            last_attempt=last_attempt
        )
```

- [ ] **Step 4: Run tests**
Run: `cd backend && pytest tests/test_practice_tests.py`
Expected: Tests should pass (may need minor updates to match new schema).

- [ ] **Step 5: Commit**
```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py backend/app/services/lesson_service.py
git commit -m "feat: persist user answers and return last attempt in practice test"
```

### Task 4: Frontend UI Refactor

**Files:**
- Modify: `frontend/src/components/features/practice-test-ui.tsx`

- [ ] **Step 1: Add viewMode state and refactor summary**
Modify `PracticeTestUI` to handle `viewMode` and show previous attempts.

```typescript
// frontend/src/components/features/practice-test-ui.tsx
// Add viewMode: 'test' | 'summary' | 'review'
// Initialize based on testData.last_attempt
const [viewMode, setViewMode] = useState<'test' | 'summary' | 'review'>(
  testData.last_attempt ? 'summary' : 'test'
);
const [results, setResults] = useState<any>(testData.last_attempt?.results || []);
const [score, setScore] = useState(testData.last_attempt?.score || 0);

// Update handleNext to setResults(response.results) and setViewMode('summary')
```

- [ ] **Step 2: Implement Review Mode UI**
Create a new section/component within `PracticeTestUI` that maps over `results` and shows the details.

- [ ] **Step 3: Add "Review Answers" button to summary**
On the finished/summary screen, add a button to switch to `'review'` mode.

- [ ] **Step 4: Commit**
```bash
git add frontend/src/components/features/practice-test-ui.tsx
git commit -m "ui: add practice test review mode and persist results"
```

### Task 5: Verification

- [ ] **Step 1: Verify E2E**
1. Log in.
2. Go to a lesson.
3. Complete practice test.
4. Verify "Review Answers" shows correctly.
5. Refresh page/revisit lesson.
6. Verify summary screen shows immediately with "Review Answers" option.
