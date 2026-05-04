from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_active_user, get_arq_pool
from arq.connections import ArqRedis
from app.infrastructure.db.models import CourseMaterialORM, PracticeTestORM, UserTestScoreORM, UserORM
from app.api.v1.schemas.course import CourseMaterialDetail
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()

class TestSubmission(BaseModel):
    score: int

@router.get("/{material_id}", response_model=CourseMaterialDetail)
def get_lesson(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
):
    material = db.execute(select(CourseMaterialORM).where(CourseMaterialORM.id == material_id)).scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Get user score if it exists
    score_rec = db.execute(
        select(UserTestScoreORM)
        .where(UserTestScoreORM.user_id == current_user.id)
        .where(UserTestScoreORM.material_id == material_id)
    ).scalar_one_or_none()
    
    # Return detail schema with score and ISO format date
    return CourseMaterialDetail(
        id=material.id,
        course_id=material.course_id,
        filename=material.filename,
        content=material.content,
        status=material.status,
        total_chunks=material.total_chunks,
        processed_chunks=material.processed_chunks,
        created_at=material.created_at.isoformat(),
        score=score_rec.score if score_rec else None
    )

@router.get("/{material_id}/test")
async def get_practice_test(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    test = db.execute(select(PracticeTestORM).where(PracticeTestORM.material_id == material_id)).scalar_one_or_none()
    if not test:
        await arq_pool.enqueue_job("generate_practice_test", material_id)
        raise HTTPException(status_code=404, detail="Test not generated yet. Generation triggered.")
    return test

@router.post("/{material_id}/test/submit")
def submit_test(
    material_id: int,
    submission: TestSubmission,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
):
    existing_score = db.execute(
        select(UserTestScoreORM)
        .where(UserTestScoreORM.user_id == current_user.id)
        .where(UserTestScoreORM.material_id == material_id)
    ).scalar_one_or_none()

    if existing_score:
        existing_score.score = max(existing_score.score, submission.score)
        existing_score.attempts += 1
        existing_score.completed_at = datetime.now(timezone.utc)
    else:
        new_score = UserTestScoreORM(
            user_id=current_user.id,
            material_id=material_id,
            score=submission.score,
            attempts=1,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(new_score)
    
    db.commit()

    # Auto-update learning plan status
    from app.infrastructure.db.models import LearningPlanORM
    plan = db.execute(
        select(LearningPlanORM)
        .where(LearningPlanORM.user_id == current_user.id)
        .where(LearningPlanORM.is_active == True)
    ).scalar_one_or_none()
    
    if plan:
        steps = list(plan.steps)
        # Sort steps by order to ensure next step logic is correct
        steps.sort(key=lambda x: x.get("order", 0))
        
        found = False
        for i, step in enumerate(steps):
            if not step.get("is_external") and step.get("resource_id") == str(material_id):
                steps[i]["status"] = "completed"
                found = True
                
                # Unlock all following external steps until the next internal one
                next_idx = i + 1
                while next_idx < len(steps):
                    # Always set the very next step to 'current' if it's upcoming
                    if steps[next_idx].get("status") == "upcoming":
                        steps[next_idx]["status"] = "current"
                    
                    # If this next step is internal, we stop (it remains 'current' but locked)
                    if not steps[next_idx].get("is_external"):
                        break
                    
                    # If it's external, we mark it as completed and keep moving
                    # because external steps don't have tests/lessons to 'finish' in our app
                    steps[next_idx]["status"] = "completed"
                    next_idx += 1
                break
        
        if found:
            # Re-assign to trigger SQLAlchemy JSON update
            plan.steps = steps
            db.add(plan)
            db.commit()

    return {"message": "Score saved successfully"}
