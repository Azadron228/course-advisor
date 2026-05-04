# Step-Based Lesson Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the Learning Plan API and enforce strict lesson isolation by moving content and tests to the `lessons` table and unifying endpoints under `/steps/{order}`.

**Architecture:** Update `LessonORM` to own its content. Refactor `PracticeTestORM` and `UserTestScoreORM` to link to `lesson_id`. Move all lesson-related API logic from `lessons.py` to `learning_plan.py` and remove the redundant router.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Pydantic.

---

### Task 1: Database Schema Refactor

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`
- Create: `backend/alembic/versions/<timestamp>_lesson_isolation_schema.py`

- [ ] **Step 1: Update ORM Models**

Modify `backend/app/infrastructure/db/models.py`:
- `LessonORM`: Add `content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)`.
- `PracticeTestORM`: Change `material_id` to `lesson_id` (ForeignKey to `lessons.id`).
- `UserTestScoreORM`: Change `material_id` to `lesson_id` (ForeignKey to `lessons.id`).

- [ ] **Step 2: Create Alembic Migration**

Run: `cd backend && uv run alembic revision -m "refactor schema for lesson isolation"`

Modify the generated file to handle the column addition and foreign key swaps. *Note: Since we are moving to an isolated model, we can start with fresh test/score associations for new plans.*

- [ ] **Step 3: Run Migration**

Run: `cd backend && uv run alembic upgrade head`

- [ ] **Step 4: Commit**

```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/*
git commit -m "db: refactor schema for lesson isolation"
```

---

### Task 2: AdvisorService & Repository Refactor

**Files:**
- Modify: `backend/app/services/advisor_service.py`
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`
- Modify: `backend/app/infrastructure/db/repositories/course_repository.py`

- [ ] **Step 1: Update `AdvisorService.generate_learning_plan`**

Modify `backend/app/services/advisor_service.py` to stop material cloning and instead copy content to the lesson record:
```python
# During lesson creation in generate_learning_plan:
original_material = self.course_repo.get_material(original_material_id)
if original_material:
    # No more CourseMaterial cloning!
    step.content = original_material.content
    step.resource_id = None # We use lesson content directly now
```

- [ ] **Step 2: Update Repository for Lesson-Based Testing**

Update `backend/app/infrastructure/db/repositories/plan_repository.py`:
- Add `get_lesson_by_order(user_id, plan_id, order)`.
- Update test/score methods to use `lesson_id` instead of `material_id`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/advisor_service.py backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "feat: refactor advisor service and repository for lesson isolation"
```

---

### Task 4: API Consolidation

**Files:**
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`
- Delete: `backend/app/api/v1/endpoints/lessons.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Implement Nested Lesson Endpoints**

Update `backend/app/api/v1/endpoints/learning_plan.py`:
- Implement `GET /steps/{step_order}` (returns `LessonDetail` with content).
- Implement `GET /steps/{step_order}/test`.
- Implement `POST /steps/{step_order}/test/submit`.

- [ ] **Step 2: Remove Redundant Lessons Router**

- Delete `backend/app/api/v1/endpoints/lessons.py`.
- Remove `lessons` router from `backend/app/api/router.py`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/endpoints/learning_plan.py backend/app/api/router.py
git rm backend/app/api/v1/endpoints/lessons.py
git commit -m "api: consolidate lesson endpoints into learning plan router"
```

---

### Task 5: Verification & Cleanup

**Files:**
- Create: `backend/tests/test_lesson_isolation.py`

- [ ] **Step 1: Write integration tests**

Verify:
- Lesson content is correctly copied during plan generation.
- Practice tests are associated with `lesson_id`.
- Scoring updates the correct lesson status in the specified plan.
- Lessons in different plans are isolated.

- [ ] **Step 2: Run all tests**

Run: `cd backend && export PYTHONPATH=. && export TESTING=True && uv run pytest`

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_lesson_isolation.py
git commit -m "test: verify lesson isolation and API consolidation"
```
