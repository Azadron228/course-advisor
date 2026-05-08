# Endpoint Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `learning_plan`, `lessons`, and `chat` endpoints to move business logic into dedicated service layers, following the project's architecture principles.

**Architecture:** Transition from fat endpoints to thin endpoints using Dependency Injection (`punq`). Extract orchestration, AI generation, and state management logic from the API layer.

**Tech Stack:** Python, FastAPI, SQLAlchemy, punq, LlamaIndex/OpenAI.

---

### Task 1: Refactor Learning Plan Logic into LearningPlanService

**Files:**
- Create: `backend/app/services/learning_plan_service.py`
- Modify: `backend/app/services/advisor_service.py`
- Modify: `backend/app/core/container.py`
- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`

- [ ] **Step 1: Create `LearningPlanService`**
Move logic for generating, listing, retrieving, and updating plans from `AdvisorService` and `learning_plan.py`.

```python
import logging
from typing import List, Optional, Any, Dict
from app.domain.recommendation.entities import LearningPlan, Student
from app.domain.identity.entities import User
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis
from app.api.v1.schemas.recommendations import (
    LearningPlanSummary, LearningPlanDetail, LessonDetail, PlanGenerateRequest
)

logger = logging.getLogger(__name__)

class LearningPlanService:
    def __init__(
        self,
        plan_repo: PlanRepository,
        course_repo: CourseRepository,
        profile_repo: ProfileRepository,
    ):
        self.plan_repo = plan_repo
        self.course_repo = course_repo
        self.profile_repo = profile_repo

    async def generate_plan(self, user: User, request: PlanGenerateRequest, arq_pool: Any = None) -> LearningPlan:
        # Move logic from AdvisorService.generate_learning_plan here
        ...

    def list_plans(self, user_id: int) -> List[LearningPlanSummary]:
        return self.plan_repo.get_all_summaries(user_id)

    def get_plan_detail(self, user_id: int, plan_id: int) -> Optional[LearningPlanDetail]:
        return self.plan_repo.get_plan_detail(user_id, plan_id)

    def delete_plan(self, user_id: int, plan_id: int) -> bool:
        return self.plan_repo.delete_plan(user_id, plan_id)

    def update_plan_step(self, user_id: int, plan_id: int, step_order: int, new_status: str) -> Optional[LearningPlan]:
        # Move logic from learning_plan.py update_learning_plan_step here
        ...
```

- [ ] **Step 2: Update `container.py` and `deps.py`**
- [ ] **Step 3: Refactor `learning_plan.py` endpoint**
- [ ] **Step 4: Remove `generate_learning_plan` from `AdvisorService`**
- [ ] **Step 5: Run tests and commit**

### Task 2: Refactor Lesson Logic into LessonService

**Files:**
- Create: `backend/app/services/lesson_service.py`
- Modify: `backend/app/core/container.py`
- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 1: Create `LessonService`**
Move content generation, test generation, and submission evaluation logic from `lessons.py`.

```python
import logging
import json
import re
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LessonORM, LearningPlanORM
from app.api.v1.schemas.recommendations import (
    LessonDetail, PracticeTestResponse, TestSubmissionResponse, TestSubmissionRequest, TestSubmissionResultItem
)
from app.domain.identity.entities import User

logger = logging.getLogger(__name__)

class LessonService:
    def __init__(self, plan_repo: PlanRepository, db: Session):
        self.plan_repo = plan_repo
        self.db = db

    async def get_lesson_detail(self, user: User, lesson_id: int) -> Optional[LessonDetail]:
        # Move content generation logic from get_lesson_detail here
        ...

    async def get_practice_test(self, user: User, lesson_id: int) -> PracticeTestResponse:
        # Move test generation logic from get_lesson_test here
        ...

    def submit_test(self, user: User, lesson_id: int, submission: TestSubmissionRequest) -> TestSubmissionResponse:
        # Move evaluation logic from submit_lesson_test here
        ...
```

- [ ] **Step 2: Update `container.py` and `deps.py`**
- [ ] **Step 3: Refactor `lessons.py` endpoint**
- [ ] **Step 4: Run tests and commit**

### Task 3: Refactor Chat Logic into ChatService

**Files:**
- Create: `backend/app/services/chat_service.py`
- Modify: `backend/app/core/container.py`
- Modify: `backend/app/api/deps.py`
- Modify: `backend/app/api/v1/endpoints/chat.py`

- [ ] **Step 1: Create `ChatService`**
Move session management and agent interaction logic from `chat.py`.

```python
import logging
import re
from typing import List, AsyncGenerator
from sqlalchemy.orm import Session
from app.infrastructure.db.repositories.chat_repository import ChatRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.cache.redis_chat import RedisChatHistory
from app.domain.identity.entities import User
from app.api.v1.schemas.recommendations import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(
        self, 
        chat_repo: ChatRepository, 
        chat_history: RedisChatHistory,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
        db: Session
    ):
        self.chat_repo = chat_repo
        self.chat_history = chat_history
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.db = db

    async def handle_chat(self, user: User, request: ChatRequest) -> ChatResponse:
        # Move logic from chat_with_advisor here
        ...

    async def stream_chat(self, user: User, request: ChatRequest) -> AsyncGenerator[str, None]:
        # Move streaming logic from chat_with_advisor here
        ...
```

- [ ] **Step 2: Update `container.py` and `deps.py`**
- [ ] **Step 3: Refactor `chat.py` endpoint**
- [ ] **Step 4: Run tests and commit**

### Task 4: Final Verification and Cleanup

- [ ] **Step 1: Run all backend tests**
`cd backend && pytest`
- [ ] **Step 2: Verify `AdvisorService` only contains recommendation logic**
- [ ] **Step 3: Commit**
