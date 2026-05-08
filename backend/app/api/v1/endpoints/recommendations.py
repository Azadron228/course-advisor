import logging
from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.schemas.recommendations import (
    Student as StudentSchema,
    UserPreference as UserPreferenceSchema,
    RecommendationResponse as RecommendationResponseSchema,
)
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    TranscriptEntry,
    ModelProvider as DomainModelProvider,
)
from app.api.v1.schemas.auth import UserPublic as User
from app.services.advisor_service import AdvisorService
from app.api.deps import (
    get_current_active_user,
    get_arq_pool,
    get_advisor_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/recommend", response_model=RecommendationResponseSchema)
async def get_recommendations(
    student: StudentSchema,
    preference: UserPreferenceSchema,
    advisor_service: AdvisorService = Depends(get_advisor_service),
    current_user: User = Depends(get_current_active_user),
):
    # Convert Schemas to Domain Entities
    transcript = [TranscriptEntry(**entry.model_dump()) for entry in student.transcript]
    student_domain = Student(
        id=student.id,
        name=student.name,
        transcript=transcript,
        current_skills=student.current_skills,
    )
    preference_domain = UserPreference(
        interest_tags=preference.interest_tags,
    )

    domain_response = await advisor_service.recommend(
        student_domain, [], preference_domain, provider=DomainModelProvider.AUTO
    )

    # Return domain response (FastAPI will convert dataclass to schema)
    return domain_response


@router.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: StudentSchema,
    preference: UserPreferenceSchema,
    arq_pool=Depends(get_arq_pool),
    current_user: User = Depends(get_current_active_user),
):
    job = await arq_pool.enqueue_job(
        "run_hybrid_recommendation",
        student.model_dump(),
        preference.model_dump(),
        "auto",
    )
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue job")
    return {"job_id": job.job_id}
