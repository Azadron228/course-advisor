# Merge Lessons API into Learning Plan API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate lesson-related endpoints into the Learning Plan API under the hierarchical path `/api/v1/learning-plan/{plan_id}/lessons/{step_order}`.

**Architecture:** `LearningPlanService` will be refactored to depend on `LessonService`. It will act as an orchestrator, resolving `step_order` to `lesson_id` and delegating lesson-specific logic to `LessonService`. API endpoints will be migrated from `/api/v1/lessons` to the hierarchical structure in `learning_plan.py`.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic

---

### Task 1: Update Dependency Injection and Service Constructor

**Files:**
- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/services/learning_plan_service.py`

- [ ] **Step 1: Update `get_learning_plan_service` in `deps.py`**

```python
# backend/app/api/deps.py

def get_learning_plan_service(
    db: Session = Depends(get_db),
    lesson_service: LessonService = Depends(get_lesson_service)
) -> LearningPlanService:
    from app.infrastructure.db.repositories.profile_repository import ProfileRepository
    from app.infrastructure.db.repositories.plan_repository import PlanRepository

    return LearningPlanService(
        profile_repo=ProfileRepository(db),
        plan_repo=PlanRepository(db),
        lesson_service=lesson_service
    )
```

- [ ] **Step 2: Update `LearningPlanService` constructor**

```python
# backend/app/services/learning_plan_service.py

from app.services.lesson_service import LessonService

class LearningPlanService:
    def __init__(
        self,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
        lesson_service: LessonService,
    ):
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.lesson_service = lesson_service
```

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/api/deps.py backend/app/services/learning_plan_service.py
git commit -m "refactor: inject LessonService into LearningPlanService"
```

---

### Task 2: Refactor Step Detail and Status Update in Service

**Files:**
- Modify: `backend/app/services/learning_plan_service.py`

- [ ] **Step 1: Refactor `get_step_detail` to be async and delegate to `lesson_service`**

```python
# backend/app/services/learning_plan_service.py

    async def get_step_detail(self, user: User, plan_id: int, step_order: int) -> Any:
        # First find the lesson by order
        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None

        # Delegate to LessonService to handle content generation and full detail retrieval
        lesson = await self.lesson_service.get_lesson_detail(user, lesson_orm.id)
        if not lesson:
            return None

        self.plan_repo.touch_plan(plan_id)
        return lesson
```

- [ ] **Step 2: Refactor `update_plan_step` to use `lesson_service`**

```python
# backend/app/services/learning_plan_service.py

    def update_plan_step(
        self, user_id: int, plan_id: int, step_order: int, new_status: str
    ) -> Optional[LearningPlan]:
        plan = self.plan_repo.get_by_id(user_id, plan_id)
        if not plan:
            return None

        lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
        if not lesson_orm:
            return None
        
        # Create a mock user for LessonService (since it expects User object)
        from app.domain.identity.entities import User as DomainUser
        user = DomainUser(id=user_id, email="", hashed_password="") # minimal user for status update

        success = self.lesson_service.update_lesson_status(user, lesson_orm.id, new_status)
        if not success:
            return None

        self.plan_repo.touch_plan(plan_id)
        return self.plan_repo.get_by_id(user_id, plan_id)
```

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/services/learning_plan_service.py
git commit -m "refactor: delegate step detail and status update to LessonService"
```

---

### Task 3: Implement Practice Test Delegation in Service

**Files:**
- Modify: `backend/app/services/learning_plan_service.py`

- [ ] **Step 1: Add `get_step_test` and `submit_step_test` methods**

```python
# backend/app/services/learning_plan_service.py

    async def get_step_test(self, user: User, plan_id: int, step_order: int) -> Any:
        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None
        
        return await self.lesson_service.get_practice_test(user, lesson_orm.id)

    def submit_step_test(self, user: User, plan_id: int, step_order: int, submission: Any) -> Any:
        lesson_orm = self.plan_repo.get_lesson_by_order(user.id, plan_id, step_order)
        if not lesson_orm:
            return None
        
        return self.lesson_service.submit_test(user, lesson_orm.id, submission)
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/services/learning_plan_service.py
git commit -m "feat: add practice test delegation to LearningPlanService"
```

---

### Task 4: Migrate API Endpoints in `learning_plan.py`

**Files:**
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`

- [ ] **Step 1: Update imports and existing endpoints**

```python
# backend/app/api/v1/endpoints/learning_plan.py

from app.api.v1.schemas.recommendations import (
    # ... existing
    PracticeTestResponse,
    TestSubmissionRequest,
    TestSubmissionResponse,
)

@router.get("/{plan_id}/lessons/{step_order}", response_model=LessonDetail)
async def get_step_detail(
    plan_id: int,
    step_order: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")

    lesson = await service.get_step_detail(current_user, plan_id, step_order) # added await and current_user
    if not lesson:
        raise HTTPException(status_code=404, detail="Step not found")

    return lesson
```

- [ ] **Step 2: Add practice test endpoints**

```python
# backend/app/api/v1/endpoints/learning_plan.py

@router.get("/{plan_id}/lessons/{step_order}/test", response_model=PracticeTestResponse)
async def get_step_test(
    plan_id: int,
    step_order: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
):
    test = await service.get_step_test(current_user, plan_id, step_order)
    if not test:
        raise HTTPException(status_code=404, detail="Practice test not found or generation failed")
    return test


@router.post("/{plan_id}/lessons/{step_order}/test/submit", response_model=TestSubmissionResponse)
async def submit_step_test(
    plan_id: int,
    step_order: int,
    submission: TestSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
):
    result = service.submit_step_test(current_user, plan_id, step_order, submission)
    if not result:
        raise HTTPException(status_code=404, detail="Test submission failed or step not found")
    return result
```

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/api/v1/endpoints/learning_plan.py
git commit -m "feat: migrate lesson endpoints to learning plan API"
```

---

### Task 5: Cleanup and Router Registration

**Files:**
- Modify: `backend/app/api/router.py`
- Delete: `backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 1: Remove lessons router from `router.py`**

```python
# backend/app/api/router.py

# Remove: from app.api.v1.endpoints import ..., lessons
# Remove: api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
```

- [ ] **Step 2: Delete `backend/app/api/v1/endpoints/lessons.py`**

Run: `rm backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/api/router.py
git rm backend/app/api/v1/endpoints/lessons.py
git commit -m "cleanup: remove standalone lessons API"
```

---

### Task 4: Verify with Tests

**Files:**
- Modify: `backend/tests/test_practice_tests.py`
- Modify: `backend/tests/test_learning_plan_redesign.py`

- [ ] **Step 1: Update `backend/tests/test_practice_tests.py` to use new endpoints**

Update all calls from `/api/v1/lessons/{lesson_id}/...` to `/api/v1/learning-plan/{plan_id}/lessons/{step_order}/...`.

- [ ] **Step 2: Run tests**

Run: `pytest backend/tests/test_practice_tests.py backend/tests/test_learning_plan_redesign.py`
Expected: ALL PASS

- [ ] **Step 3: Commit changes**

```bash
git add backend/tests/
git commit -m "test: update tests for merged learning plan API"
```
