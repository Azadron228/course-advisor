# Database Migration: Add Answers to UserTestScore Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new column `answers` to the `user_test_scores` table to persist user's submitted answers for practice tests.

**Architecture:** Update the SQLAlchemy ORM model `UserTestScoreORM` and create a corresponding Alembic migration to keep the database schema in sync.

**Tech Stack:** Python, SQLAlchemy, Alembic.

---

### Task 1: Update the UserTestScoreORM model

**Files:**
- Modify: `backend/app/infrastructure/db/models.py:120-132`

- [ ] **Step 1: Add the `answers` column to `UserTestScoreORM`**

Modify `backend/app/infrastructure/db/models.py`:
```python
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

### Task 2: Create the Alembic migration

**Files:**
- Create: `backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py`

- [ ] **Step 1: Create the new migration file**

Create `backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py`:
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

### Task 3: Run migration and verify

- [ ] **Step 1: Run the migration**

Run: `cd backend && alembic upgrade head`
Expected: Successfully upgraded to `a7f8e9c1d2b3`.

- [ ] **Step 2: Verify the table schema**

Run: `sqlite3 backend/test.db ".schema user_test_scores"` (assuming SQLite based on `test.db` in file list)
Expected: `answers` column is present in the table definition.

### Task 4: Commit

- [ ] **Step 1: Commit the changes**

Run:
```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/2026_05_14_add_answers_to_test_scores.py
git commit -m "db: add answers column to user_test_scores"
```
