# Learning Plan Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Learning Plan business logic from `AdvisorService` and API endpoints into a dedicated `LearningPlanService`.

**Architecture:** Moving business logic to a specialized service layer (`LearningPlanService`) to improve modularity, testability, and keep API endpoints thin. The new service will handle generation, listing, retrieval, and updates of learning plans.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Punq (DI).

---

### Task 1: Create LearningPlanService

**Files:**
- Create: `backend/app/services/learning_plan_service.py`

- [ ] **Step 1: Create `LearningPlanService` and move `generate_plan` logic**

```python
import logging
from typing import List, Optional, Any, Dict
import re
from sqlalchemy import select

from app.domain.identity.entities import User
from app.domain.recommendation.entities import (
    Student,
    ModelProvider,
    LearningPlan,
)
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.ai.agent import get_model
from app.infrastructure.ai.analysis_agent import generate_global_analysis
from app.infrastructure.db.models import UserTestScoreORM, LessonORM

logger = logging.getLogger(__name__)

class LearningPlanService:
    def __init__(
        self,
        course_repo: CourseRepository,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
    ):
        self.course_repo = course_repo
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo

    async def generate_plan(self, user: User, request: Optional[Any] = None, arq_pool: Optional[Any] = None) -> LearningPlan:
        """
        Generate a learning plan for a user using AI analysis of their profile and available courses.
        Saves the plan to the database and returns it.
        """
        if user.id is None:
            raise ValueError("User ID cannot be None")

        # 1. Gather profile data from repositories
        skills = self.profile_repo.get_skills(user.id)
        
        # Use transcript from request if provided, otherwise from DB
        if request and hasattr(request, 'transcript') and request.transcript:
            transcript = request.transcript
        else:
            transcript = self.profile_repo.get_transcript(user.id)

        student = Student(
            id=str(user.id),
            name=user.full_name or "Student",
            transcript=transcript,
            current_skills=[s.skill_name for s in skills],
        )

        # 2. Get all available internal courses
        courses = self.course_repo.get_all()

        # 3. AI Generation via Analysis Agent
        llm = get_model(ModelProvider.AUTO)
        
        goal = request.goal if request else (user.career_goal or "General Growth")
        skill_level = request.skill_level if request else "Beginner"
        learning_style = request.learning_style if request else "Practical"
        study_time = request.study_time if request else 10
        interests = request.interests if request else []
        language = request.language if request and hasattr(request, 'language') else "en"

        goal_msg = (
            f"Goal: {goal}. "
            f"Skill level: {skill_level}. Learning style: {learning_style}. "
            f"Study time: {study_time} hours/week. Interests: {', '.join(interests)}."
        )
        
        logger.info(f"Generating learning plan for goal: {goal}")
        try:
            parsed = await generate_global_analysis(llm, student, courses, goal_msg, language)
            logger.info(f"Successfully generated analysis for {goal}")
            
            # Use AI generated title if available
            final_title = parsed.title if hasattr(parsed, 'title') else goal
            
            # Ensure the first step is 'current' so it's not locked
            if parsed.learning_path:
                # Sort by order just in case the LLM didn't
                parsed.learning_path.sort(key=lambda x: x.order)
                parsed.learning_path[0].status = "current"
        except Exception as gen_err:
            logger.error(f"AI Generation failed: {gen_err}")
            raise

        # 4. Populate lessons with content and check for existing scores BEFORE creating the plan
        try:
            self.plan_repo.deactivate_all_plans(user.id)
            
            # Populate lessons with content and check for existing scores
            for step in parsed.learning_path:
                if not step.is_external and step.resource_id:
                    try:
                        # Extract first integer from step.resource_id
                        match = re.search(r'\d+', str(step.resource_id))
                        if not match:
                            raise ValueError(f"Could not extract integer from resource_id: {step.resource_id}")
                        
                        original_material_id = int(match.group())
                        original_material = self.course_repo.get_material(original_material_id)
                        
                        if original_material:
                            # Check if user already passed this material in ANY previous lesson
                            existing_score = self.plan_repo.db.execute(
                                select(UserTestScoreORM)
                                .join(LessonORM)
                                .where(UserTestScoreORM.user_id == user.id)
                                .where(LessonORM.material_id == original_material_id)
                                .order_by(UserTestScoreORM.score.desc())
                            ).scalars().first()
                            
                            if existing_score and existing_score.score >= 70:
                                step.status = "completed"
                                logger.info(f"Marked step {step.title} as completed based on previous score {existing_score.score}%")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to process material for step {step.title}: {e}")

            # Ensure the first non-completed step is 'current'
            found_current = False
            for step in parsed.learning_path:
                if step.status != "completed":
                    if not found_current:
                        step.status = "current"
                        found_current = True
                    else:
                        step.status = "upcoming"
            
            # Initial create
            initial_plan = LearningPlan(
                id=None,
                goal=final_title,
                steps=parsed.learning_path,
                is_active=True,
                skill_level=skill_level,
                learning_style=learning_style,
                study_time=study_time,
                interests=interests,
            )
            saved_plan = self.plan_repo.create_plan(user.id, initial_plan)
            logger.info(f"Successfully saved learning plan {saved_plan.id}")

            # 5. Copy scores to the new lessons
            for step in saved_plan.steps:
                # 5.1 Check for existing scores and copy them (for internal material matches)
                if not step.is_external and step.resource_id:
                    try:
                        match = re.search(r'\d+', str(step.resource_id))
                        if not match:
                            continue
                        original_material_id = int(match.group())
                        
                        existing_score = self.plan_repo.db.execute(
                            select(UserTestScoreORM)
                            .join(LessonORM)
                            .where(UserTestScoreORM.user_id == user.id)
                            .where(LessonORM.material_id == original_material_id)
                            .order_by(UserTestScoreORM.score.desc())
                        ).scalars().first()

                        if existing_score:
                            new_score = UserTestScoreORM(
                                user_id=user.id,
                                lesson_id=step.id,
                                score=existing_score.score,
                                attempts=existing_score.attempts,
                                completed_at=existing_score.completed_at
                            )
                            self.plan_repo.db.add(new_score)
                            logger.info(f"Copied score {existing_score.score}% to new lesson {step.id}")
                    except (ValueError, TypeError):
                        pass
            
            self.plan_repo.db.commit()
            return saved_plan
        except Exception as db_err:
            logger.error(f"Failed to persist learning plan: {db_err}")
            raise

    def list_plans(self, user_id: int) -> List[Any]:
        return self.plan_repo.get_all_summaries(user_id)

    def get_plan_detail(self, user_id: int, plan_id: int) -> Any:
        plan = self.plan_repo.get_plan_detail(user_id, plan_id)
        if not plan:
            return None
        return plan

    def delete_plan(self, user_id: int, plan_id: int) -> bool:
        return self.plan_repo.delete_plan(user_id, plan_id)

    def get_step_detail(self, user_id: int, plan_id: int, step_order: int) -> Any:
        # First find the lesson by order
        lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
        if not lesson_orm:
            return None
        
        lesson = self.plan_repo.get_lesson_with_materials(user_id, plan_id, lesson_orm.id)
        if not lesson:
            return None
        
        self.plan_repo.touch_plan(plan_id)
        return lesson

    def update_plan_step(self, user_id: int, plan_id: int, step_order: int, new_status: str) -> Optional[LearningPlan]:
        plan = self.plan_repo.get_by_id(user_id, plan_id)
        if not plan:
            return None
        
        if new_status == "completed":
            lesson_orm = self.plan_repo.get_lesson_by_order(user_id, plan_id, step_order)
            if not lesson_orm:
                return None
            self.plan_repo.complete_lesson(user_id, lesson_orm.id)
        else:
            # Update the specific step status
            updated_steps = sorted(plan.steps, key=lambda x: x.order)
            found_idx = -1
            for i, step in enumerate(updated_steps):
                if step.order == step_order:
                    updated_steps[i] = step.model_copy(update={"status": new_status})
                    found_idx = i
                    break
                    
            if found_idx == -1:
                return None
            
            updated_plan = plan.model_copy(update={"steps": updated_steps})
            self.plan_repo.update_plan(user_id, updated_plan)
        
        self.plan_repo.touch_plan(plan_id)
        return self.plan_repo.get_by_id(user_id, plan_id)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/learning_plan_service.py
git commit -m "feat: create LearningPlanService"
```

### Task 2: Register LearningPlanService in Container

**Files:**
- Modify: `backend/app/core/container.py`

- [ ] **Step 1: Update `container.py` to register `LearningPlanService`**

```python
# ... existing imports
from app.services.advisor_service import AdvisorService
from app.services.learning_plan_service import LearningPlanService # Add this

# ...
    # Application Services
    container.register(AdvisorService)
    container.register(LearningPlanService) # Add this

    return container
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/container.py
git commit -m "refactor: register LearningPlanService in container"
```

### Task 3: Update Dependencies

**Files:**
- Modify: `backend/app/api/deps.py`

- [ ] **Step 1: Add `get_learning_plan_service` to `deps.py`**

```python
# ... existing imports
from app.services.advisor_service import AdvisorService
from app.services.learning_plan_service import LearningPlanService # Add this
# ...

def get_advisor_service(service: AdvisorService = Depends(get_service(AdvisorService))):
    return service

# Add this
def get_learning_plan_service(service: LearningPlanService = Depends(get_service(LearningPlanService))):
    return service
# ...
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/deps.py
git commit -m "refactor: add get_learning_plan_service dependency"
```

### Task 4: Refactor Learning Plan Endpoints

**Files:**
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`

- [ ] **Step 1: Refactor endpoints to use `LearningPlanService`**

```python
from fastapi import APIRouter, Depends, HTTPException, Body
from app.api.deps import get_current_active_user, get_learning_plan_service, get_arq_pool
from app.domain.identity.entities import User
from app.services.learning_plan_service import LearningPlanService
from app.api.v1.schemas.recommendations import (
    LearningPlan, 
    PlanGenerateRequest, 
    LearningPlanSummary, 
    LearningPlanDetail,
    LessonDetail
)
from typing import Dict, List

router = APIRouter()

@router.get("/", response_model=List[LearningPlanSummary])
async def list_learning_plans(
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service)
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    return service.list_plans(current_user.id)

@router.get("/{plan_id}", response_model=LearningPlanDetail)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service)
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    plan = service.get_plan_detail(current_user.id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.delete("/{plan_id}", status_code=204)
async def delete_learning_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service)
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    deleted = service.delete_plan(current_user.id, plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    
    return None

@router.get("/{plan_id}/steps/{step_order}", response_model=LessonDetail)
async def get_step_detail(
    plan_id: int,
    step_order: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service)
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    lesson = service.get_step_detail(current_user.id, plan_id, step_order)
    if not lesson:
        raise HTTPException(status_code=404, detail="Step not found")
    
    return lesson

@router.post("/generate", response_model=LearningPlan)
async def generate_learning_plan(
    request: PlanGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
    arq_pool = Depends(get_arq_pool)
):
    return await service.generate_plan(current_user, request, arq_pool)

@router.patch("/{plan_id}/steps/{step_order}", response_model=LearningPlan)
async def update_learning_plan_step(
    plan_id: int,
    step_order: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service)
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    updated_plan = service.update_plan_step(current_user.id, plan_id, step_order, new_status)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Step or Plan not found")
        
    return updated_plan
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/endpoints/learning_plan.py
git commit -m "refactor: use LearningPlanService in endpoints"
```

### Task 5: Clean up AdvisorService

**Files:**
- Modify: `backend/app/services/advisor_service.py`

- [ ] **Step 1: Remove `generate_learning_plan` and unused imports**

```python
# Remove LearningPlan from imports if unused elsewhere
# Remove generate_learning_plan method
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/advisor_service.py
git commit -m "refactor: remove generate_learning_plan from AdvisorService"
```

### Task 6: Verification

- [ ] **Step 1: Run tests**

Run: `pytest backend/tests/test_learning_plan_redesign.py -v`
Expected: PASS
