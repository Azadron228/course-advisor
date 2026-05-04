# Learning Plan API Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Learning Plan API to improve performance by separating plan metadata from lesson materials and tracking user interaction time for sorting.

**Architecture:** Introduce `Summary` and `Detail` schemas for both Plans and Lessons. Add a `last_interacted_at` column to the `learning_plans` table and update it on key user actions. Implement a dedicated endpoint for fetching lesson materials on-demand.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Pydantic.

---

### Task 1: Database Migration

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`
- Create: `backend/alembic/versions/<timestamp>_add_last_interacted_at.py`

- [ ] **Step 1: Update ORM Model**

Modify `backend/app/infrastructure/db/models.py`:
```python
class LearningPlanORM(Base):
    # ... existing fields ...
    last_interacted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
```

- [ ] **Step 2: Create Alembic Migration**

Run: `cd backend && uv run alembic revision -m "add last_interacted_at to learning_plans"`

Modify the generated file to set a default for existing rows:
```python
def upgrade() -> None:
    op.add_column('learning_plans', sa.Column('last_interacted_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

def downgrade() -> None:
    op.drop_column('learning_plans', 'last_interacted_at')
```

- [ ] **Step 3: Run Migration**

Run: `cd backend && uv run alembic upgrade head`

- [ ] **Step 4: Commit**

```bash
git add backend/app/infrastructure/db/models.py backend/alembic/versions/*
git commit -m "db: add last_interacted_at to learning_plans"
```

---

### Task 2: Schema Refactor

**Files:**
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Define new schemas**

Replace/Add in `backend/app/api/v1/schemas/recommendations.py`:
```python
class LessonSummary(BaseModel):
    id: int
    order: int
    title: str
    description: str
    status: str
    score: Optional[int] = None
    is_external: bool
    model_config = ConfigDict(from_attributes=True)

class LessonDetail(LessonSummary):
    materials: List[LearningMaterial]
    external_url: Optional[str] = None

class LearningPlanSummary(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    step_count: int
    model_config = ConfigDict(from_attributes=True)

class LearningPlanDetail(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    steps: List[LessonSummary]
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/schemas/recommendations.py
git commit -m "schema: add learning plan summary and detail schemas"
```

---

### Task 3: Repository Enhancements

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Update `get_all_plans` with sorting and count**

```python
    def get_all_summaries(self, user_id: int) -> List[LearningPlanSummary]:
        from sqlalchemy import func
        
        # Subquery to count lessons per plan
        count_subquery = (
            select(LessonORM.plan_id, func.count(LessonORM.id).label("step_count"))
            .group_by(LessonORM.plan_id)
            .subquery()
        )

        query = (
            select(LearningPlanORM, count_subquery.c.step_count)
            .outerjoin(count_subquery, LearningPlanORM.id == count_subquery.c.plan_id)
            .where(LearningPlanORM.user_id == user_id)
            .order_by(LearningPlanORM.last_interacted_at.desc())
        )
        
        results = self.db.execute(query).all()
        
        return [
            LearningPlanSummary(
                id=p.id,
                goal=p.goal,
                is_active=p.is_active,
                last_interacted_at=p.last_interacted_at,
                step_count=step_count or 0
            )
            for p, step_count in results
        ]
```

- [ ] **Step 2: Update `get_by_id` to return Detail without materials**

```python
    def get_plan_detail(self, user_id: int, plan_id: int) -> Optional[LearningPlanDetail]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o:
            return None
            
        # Collect material IDs for scores
        material_ids = [l.material_id for l in o.lessons if l.material_id]
        scores_map = {}
        if material_ids:
            scores = self.db.execute(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == user_id)
                .where(UserTestScoreORM.material_id.in_(material_ids))
            ).scalars().all()
            scores_map = {s.material_id: s.score for s in scores}

        return LearningPlanDetail(
            id=o.id,
            goal=o.goal,
            is_active=o.is_active,
            last_interacted_at=o.last_interacted_at,
            steps=[
                LessonSummary(
                    id=l.id,
                    order=l.order,
                    title=l.title,
                    description=l.description,
                    status=l.status,
                    is_external=l.is_external,
                    score=scores_map.get(l.material_id) if l.material_id else None
                )
                for l in o.lessons
            ]
        )
```

- [ ] **Step 3: Implement `get_lesson_with_materials`**

```python
    def get_lesson_with_materials(self, user_id: int, plan_id: int, lesson_id: int) -> Optional[LessonDetail]:
        l = self.db.scalar(
            select(LessonORM)
            .join(LearningPlanORM)
            .where(LessonORM.id == lesson_id)
            .where(LessonORM.plan_id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not l:
            return None

        score = None
        if l.material_id:
            score_rec = self.db.scalar(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == user_id)
                .where(UserTestScoreORM.material_id == l.material_id)
            )
            score = score_rec.score if score_rec else None

        return LessonDetail(
            id=l.id,
            order=l.order,
            title=l.title,
            description=l.description,
            status=l.status,
            is_external=l.is_external,
            external_url=l.external_url,
            score=score,
            materials=[LearningMaterial(**m) for m in l.additional_resources]
        )
```

- [ ] **Step 4: Implement `touch_plan` (Update Interaction Time)**

```python
    def touch_plan(self, plan_id: int):
        self.db.execute(
            update(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .values(last_interacted_at=datetime.now(timezone.utc))
        )
        self.db.commit()
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "repo: implement summary and detail methods for learning plans"
```

---

### Task 4: API Refactor & Interaction Triggers

**Files:**
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`
- Modify: `backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 1: Update `GET /` and `GET /{plan_id}`**

Update `backend/app/api/v1/endpoints/learning_plan.py`:
```python
@router.get("/", response_model=List[LearningPlanSummary])
async def list_learning_plans(
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    return plan_repo.get_all_summaries(current_user.id)

@router.get("/{plan_id}", response_model=LearningPlanDetail)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    plan = plan_repo.get_plan_detail(current_user.id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
```

- [ ] **Step 2: Add `GET /{plan_id}/lessons/{lesson_id}`**

Add to `backend/app/api/v1/endpoints/learning_plan.py`:
```python
@router.get("/{plan_id}/lessons/{lesson_id}", response_model=LessonDetail)
async def get_lesson_detail(
    plan_id: int,
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    lesson = plan_repo.get_lesson_with_materials(current_user.id, plan_id, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Update interaction time when a lesson is viewed
    plan_repo.touch_plan(plan_id)
    
    return lesson
```

- [ ] **Step 3: Update Interaction Time on Status Change**

Update `update_learning_plan_step` in `learning_plan.py`:
```python
    # After updating plan steps...
    updated_plan = plan.model_copy(update={"steps": updated_steps})
    result = plan_repo.update_plan(current_user.id, updated_plan)
    plan_repo.touch_plan(plan_id)
    return result
```

Update `submit_test` in `backend/app/api/v1/endpoints/lessons.py`:
```python
    if plan:
        # ... existing logic ...
        if found:
            db.commit()
            # New line: update interaction time
            from app.infrastructure.db.repositories.plan_repository import PlanRepository
            PlanRepository(db).touch_plan(plan.id)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/learning_plan.py backend/app/api/v1/endpoints/lessons.py
git commit -m "api: refactor learning plan endpoints and add interaction triggers"
```

---

### Task 5: Verification

**Files:**
- Create: `backend/tests/test_learning_plan_redesign.py`

- [ ] **Step 1: Write integration tests**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_plan_summary_list(client: TestClient, active_user_token_headers):
    r = client.get("/api/v1/learning-plan/", headers=active_user_token_headers)
    assert r.status_code == 200
    plans = r.json()
    assert isinstance(plans, list)
    if plans:
        assert "step_count" in plans[0]
        assert "steps" not in plans[0]

def test_plan_detail_no_materials(client: TestClient, active_user_token_headers):
    # Fetch first plan
    r_list = client.get("/api/v1/learning-plan/", headers=active_user_token_headers)
    plans = r_list.json()
    if not plans: return

    plan_id = plans[0]["id"]
    r = client.get(f"/api/v1/learning-plan/{plan_id}", headers=active_user_token_headers)
    assert r.status_code == 200
    plan = r.json()
    assert "steps" in plan
    if plan["steps"]:
        assert "materials" not in plan["steps"][0]

def test_lesson_detail_with_materials(client: TestClient, active_user_token_headers):
    # Fetch first plan then its first lesson
    r_list = client.get("/api/v1/learning-plan/", headers=active_user_token_headers)
    plans = r_list.json()
    if not plans: return

    plan_id = plans[0]["id"]
    r_plan = client.get(f"/api/v1/learning-plan/{plan_id}", headers=active_user_token_headers)
    plan = r_plan.json()
    if not plan["steps"]: return

    lesson_id = plan["steps"][0]["id"]
    r = client.get(f"/api/v1/learning-plan/{plan_id}/lessons/{lesson_id}", headers=active_user_token_headers)
    assert r.status_code == 200
    lesson = r.json()
    assert "materials" in lesson
```

- [ ] **Step 2: Run tests**

Run: `cd backend && uv run pytest tests/test_learning_plan_redesign.py`

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_learning_plan_redesign.py
git commit -m "test: add integration tests for learning plan API redesign"
```
