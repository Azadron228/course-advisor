from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any, Dict

from app.api.deps import get_db, get_current_active_user, get_arq_pool
from arq.connections import ArqRedis
from app.infrastructure.db.models import CourseMaterialORM, PracticeTestORM, UserTestScoreORM, UserORM
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()

class TestSubmission(BaseModel):
    score: int

@router.get("/{material_id}")
def get_lesson(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_active_user),
):
    material = db.execute(select(CourseMaterialORM).where(CourseMaterialORM.id == material_id)).scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

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
    return {"message": "Score saved successfully"}
