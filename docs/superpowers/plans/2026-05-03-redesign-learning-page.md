# Redesigned Learning Page Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the learning experience with dedicated lesson pages, anchored AI chat, and background-generated practice tests.

**Architecture:** 
- Backend: New tables for tests and scores, worker tasks for AI generation.
- Frontend: New `/[locale]/lesson/[id]` and `/[locale]/lesson/[id]/test` routes, shared UI components for chat and tests.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL (pgvector), Next.js, Tailwind CSS, OpenAI/Gemini API.

---

### Task 1: Database Schema Updates

**Files:**
- Create: `backend/alembic/versions/2026_05_03_add_practice_tests_and_scores.py`
- Modify: `backend/app/infrastructure/db/models.py`

- [ ] **Step 1: Update models.py with new ORM classes**

```python
class PracticeTestORM(Base):
    __tablename__ = "practice_tests"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("course_materials.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)  # questions, options, answers
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserTestScoreORM(Base):
    __tablename__ = "user_test_scores"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    material_id: Mapped[int] = mapped_column(ForeignKey("course_materials.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 2: Generate and run alembic migration**

Run: `uv run alembic revision --autogenerate -m "add practice tests and scores"`
Run: `uv run alembic upgrade head`

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/*
git commit -m "db: add practice_tests and user_test_scores tables"
```

### Task 2: Backend Entities and Lesson Endpoints

**Files:**
- Create: `backend/app/domain/catalog/entities.py` (Update)
- Create: `backend/app/api/v1/endpoints/lessons.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Add new endpoints for Lesson and Test**

Implement `GET /lessons/{material_id}`, `GET /lessons/{material_id}/test`, `POST /lessons/{material_id}/test/submit`.

- [ ] **Step 2: Register router**

Add `lessons.router` to `backend/app/api/router.py`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/lessons.py backend/app/api/router.py
git commit -m "feat: add lesson and test endpoints"
```

### Task 3: Background Test Generation Task

**Files:**
- Create: `backend/app/tasks/test_tasks.py`
- Modify: `backend/app/worker.py`

- [ ] **Step 1: Implement AI test generation logic using LLM**

Use `llama-index` or direct OpenAI call to generate questions from material content.

- [ ] **Step 2: Integrate task into lesson loading**

When `GET /lessons/{material_id}` is called, trigger background generation if test doesn't exist.

- [ ] **Step 3: Commit**

```bash
git add backend/app/tasks/test_tasks.py backend/app/worker.py
git commit -m "feat: add background test generation task"
```

### Task 4: Frontend Lesson Page UI

**Files:**
- Create: `frontend/src/app/[locale]/lesson/[id]/page.tsx`
- Create: `frontend/src/components/features/lesson-sidebar-chat.tsx`

- [ ] **Step 1: Build the lesson page layout with 70/30 split**
- [ ] **Step 2: Implement anchored AI chat sidebar**
- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/[locale]/lesson/
git commit -m "feat: implement lesson page UI and anchored chat"
```

### Task 5: Practice Test Page and Score Tracking

**Files:**
- Create: `frontend/src/app/[locale]/lesson/[id]/test/page.tsx`
- Create: `frontend/src/components/features/practice-test-ui.tsx`

- [ ] **Step 1: Implement the immersive test UI**
- [ ] **Step 2: Handle submission and show results**
- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/[locale]/lesson/
git commit -m "feat: implement practice test UI and results"
```
