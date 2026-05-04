from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.api.deps import get_current_active_user, get_service, get_arq_pool, get_db
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LearningPlanORM, LessonORM, PracticeTestORM, UserTestScoreORM
from app.api.v1.schemas.recommendations import LessonDetail
from app.domain.identity.entities import User
from typing import Dict
from pydantic import BaseModel
from datetime import datetime, timezone
from arq.connections import ArqRedis

router = APIRouter()

class TestSubmission(BaseModel):
    score: int

@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson_detail(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    lesson = plan_repo.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    plan = plan_repo.get_by_id(current_user.id, lesson.plan_id)
    if not plan:
        raise HTTPException(status_code=403, detail="Not authorized to view this lesson")
        
    lesson_detail = plan_repo.get_lesson_with_materials(current_user.id, lesson.plan_id, lesson_id)
    if not lesson_detail:
        raise HTTPException(status_code=404, detail="Lesson detail not found")
        
    return lesson_detail

@router.get("/{lesson_id}/test")
async def get_lesson_test(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository)),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = plan_repo.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    plan = plan_repo.get_by_id(current_user.id, lesson.plan_id)
    if not plan:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if lesson.is_external or not lesson.material_id:
        raise HTTPException(status_code=400, detail="External steps do not have practice tests")

    test = db.execute(select(PracticeTestORM).where(PracticeTestORM.lesson_id == lesson_id)).scalar_one_or_none()
    if not test:
        await arq_pool.enqueue_job("generate_practice_test", lesson_id)
        raise HTTPException(status_code=404, detail="Test not generated yet. Generation triggered.")
    return test

@router.post("/{lesson_id}/test/submit")
def submit_lesson_test(
    lesson_id: int,
    submission: TestSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository)),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Check ownership
    plan_orm = db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == lesson.plan_id).where(LearningPlanORM.user_id == current_user.id))
    if not plan_orm:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_score = db.execute(
        select(UserTestScoreORM)
        .where(UserTestScoreORM.user_id == current_user.id)
        .where(UserTestScoreORM.lesson_id == lesson_id)
    ).scalar_one_or_none()

    if existing_score:
        existing_score.score = max(existing_score.score, submission.score)
        existing_score.attempts += 1
        existing_score.completed_at = datetime.now(timezone.utc)
    else:
        new_score = UserTestScoreORM(
            user_id=current_user.id,
            lesson_id=lesson_id,
            score=submission.score,
            attempts=1,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(new_score)
    
    # Update lesson status
    lesson.status = "completed"
    
    # Auto-unlock logic
    # Need to reload plan with lessons to ensure correct order
    plan = db.scalar(
        select(LearningPlanORM)
        .options(selectinload(LearningPlanORM.lessons))
        .where(LearningPlanORM.id == lesson.plan_id)
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
    plan_repo.touch_plan(lesson.plan_id)

    return {"message": "Score saved successfully"}

@router.patch("/{lesson_id}")
async def update_lesson(
    lesson_id: int,
    status_update: Dict[str, str] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Check ownership
    plan_orm = db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == lesson.plan_id).where(LearningPlanORM.user_id == current_user.id))
    if not plan_orm:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    lesson.status = new_status
    
    # Auto-unlock next step if completed
    if new_status == "completed":
        plan = db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == lesson.plan_id)
        )
        if plan:
            found_idx = -1
            for i, lesson_orm in enumerate(plan.lessons):
                if lesson_orm.id == lesson.id:
                    found_idx = i
                    break
            
            if found_idx != -1 and found_idx + 1 < len(plan.lessons):
                next_lesson = plan.lessons[found_idx + 1]
                if next_lesson.status == "upcoming":
                    next_lesson.status = "current"
        
    db.commit()
    plan_repo.touch_plan(lesson.plan_id)
    return {"message": "Status updated"}
