from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from arq.jobs import Job, JobStatus
from ...schemas.course import Student, UserPreference
from ...schemas.recommendation import RecommendationResponse
from ...schemas.internal import ModelProvider
from ...schemas.user import UserBase as User
from ...crud import get_all_courses
from ...scoring.orchestrator import HybridScorer
from ..deps import get_db, get_current_active_user, get_arq_pool

router = APIRouter()
scorer = HybridScorer()

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    courses = get_all_courses(db)
    if not courses:
         return RecommendationResponse(results=[])
    return await scorer.recommend(db, student, courses, preference, provider=ModelProvider.AUTO)


@router.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: Student,
    preference: UserPreference,
    arq_pool = Depends(get_arq_pool),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = await arq_pool.enqueue_job(
        'run_hybrid_recommendation',
        student.model_dump(),
        [c.model_dump() for c in get_all_courses(db)],
        preference.model_dump()
    )
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue job")
    return {"job_id": job.job_id}


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    arq_pool = Depends(get_arq_pool),
    current_user: User = Depends(get_current_active_user)
):
    job = Job(job_id, arq_pool)
    try:
        status_val = await job.status()
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if status_val == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")
        
    info = await job.info()
    return {
        "job_id": job.job_id,
        "status": status_val.value if hasattr(status_val, 'value') else str(status_val),
        "result": await job.result(timeout=0) if status_val == JobStatus.complete else None,
        "enqueued_at": info.enqueue_time if info else None,
        "started_at": info.start_time if info else None,
        "ended_at": None
    }
