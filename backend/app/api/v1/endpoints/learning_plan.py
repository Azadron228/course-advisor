from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.api.deps import get_current_active_user, get_advisor_service, get_service, get_arq_pool, get_db
from app.domain.identity.entities import User
from app.services.advisor_service import AdvisorService
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LearningPlanORM, PracticeTestORM, UserTestScoreORM
from app.api.v1.schemas.recommendations import (
    LearningPlan, 
    PlanGenerateRequest, 
    LearningPlanSummary, 
    LearningPlanDetail,
    LessonDetail
)
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime, timezone
from arq.connections import ArqRedis

router = APIRouter()

class TestSubmission(BaseModel):
    score: int

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

@router.get("/{plan_id}/steps/{step_order}", response_model=LessonDetail)
async def get_step_detail(
    plan_id: int,
    step_order: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    # First find the lesson by order
    lesson_orm = plan_repo.get_lesson_by_order(current_user.id, plan_id, step_order)
    if not lesson_orm:
        raise HTTPException(status_code=404, detail="Step not found")
    
    lesson = plan_repo.get_lesson_with_materials(current_user.id, plan_id, lesson_orm.id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    plan_repo.touch_plan(plan_id)
    return lesson

@router.get("/{plan_id}/steps/{step_order}/test")
async def get_step_test(
    plan_id: int,
    step_order: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository)),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = plan_repo.get_lesson_by_order(current_user.id, plan_id, step_order)
    if not lesson:
        raise HTTPException(status_code=404, detail="Step not found")
    
    if lesson.is_external or not lesson.material_id:
        raise HTTPException(status_code=400, detail="External steps do not have practice tests")

    test = db.execute(select(PracticeTestORM).where(PracticeTestORM.lesson_id == lesson.id)).scalar_one_or_none()
    if not test:
        await arq_pool.enqueue_job("generate_practice_test", lesson.material_id)
        raise HTTPException(status_code=404, detail="Test not generated yet. Generation triggered.")
    return test

@router.post("/{plan_id}/steps/{step_order}/test/submit")
def submit_step_test(
    plan_id: int,
    step_order: int,
    submission: TestSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository)),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = plan_repo.get_lesson_by_order(current_user.id, plan_id, step_order)
    if not lesson:
        raise HTTPException(status_code=404, detail="Step not found")
    
    if lesson.is_external or not lesson.material_id:
        raise HTTPException(status_code=400, detail="External steps do not have practice tests")

    existing_score = db.execute(
        select(UserTestScoreORM)
        .where(UserTestScoreORM.user_id == current_user.id)
        .where(UserTestScoreORM.lesson_id == lesson.id)
    ).scalar_one_or_none()

    if existing_score:
        existing_score.score = max(existing_score.score, submission.score)
        existing_score.attempts += 1
        existing_score.completed_at = datetime.now(timezone.utc)
    else:
        new_score = UserTestScoreORM(
            user_id=current_user.id,
            lesson_id=lesson.id,
            score=submission.score,
            attempts=1,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(new_score)
    
    # Update lesson status
    lesson.status = "completed"
    
    # Auto-unlock logic
    plan = db.scalar(
        select(LearningPlanORM)
        .options(selectinload(LearningPlanORM.lessons))
        .where(LearningPlanORM.id == plan_id)
        .where(LearningPlanORM.user_id == current_user.id)
    )
    
    if plan:
        found_idx = -1
        for i, lesson_orm in enumerate(plan.lessons):
            if lesson_orm.id == lesson.id:
                found_idx = i
                break
        
        if found_idx != -1:
            next_idx = found_idx + 1
            while next_idx < len(plan.lessons):
                next_lesson = plan.lessons[next_idx]
                if next_lesson.status == "upcoming":
                    next_lesson.status = "current"
                
                if not next_lesson.is_external:
                    break
                
                next_lesson.status = "completed"
                next_idx += 1
    
    db.commit()
    plan_repo.touch_plan(plan_id)

    return {"message": "Score saved successfully"}

@router.post("/generate", response_model=LearningPlan)
async def generate_learning_plan(
    request: PlanGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    advisor_service: AdvisorService = Depends(get_advisor_service),
    arq_pool = Depends(get_arq_pool)
):
    return await advisor_service.generate_learning_plan(current_user, request, arq_pool)

@router.patch("/{plan_id}/steps/{step_order}", response_model=LearningPlan)
async def update_learning_plan_step(
    plan_id: int,
    step_order: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    plan = plan_repo.get_by_id(current_user.id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    # Update the specific step status
    updated_steps = sorted(plan.steps, key=lambda x: x.order)
    found_idx = -1
    for i, step in enumerate(updated_steps):
        if step.order == step_order:
            updated_steps[i] = step.model_copy(update={"status": new_status})
            found_idx = i
            break
            
    if found_idx == -1:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Auto-unlock next step if completed
    if new_status == "completed" and found_idx + 1 < len(updated_steps):
        next_step = updated_steps[found_idx + 1]
        if next_step.status == "upcoming":
            updated_steps[found_idx + 1] = next_step.model_copy(update={"status": "current"})
        
    updated_plan = plan.model_copy(update={"steps": updated_steps})
    result = plan_repo.update_plan(current_user.id, updated_plan)
    
    plan_repo.touch_plan(plan_id)
    return result
