from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user, get_advisor_service, get_service
from app.domain.identity.entities import User
from app.services.advisor_service import AdvisorService
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.api.v1.schemas.recommendations import LearningPlan

router = APIRouter()

@router.get("/", response_model=LearningPlan)
async def get_learning_plan(
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    plan = plan_repo.get_active_plan(current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active learning plan found")
    return plan

@router.post("/generate", response_model=LearningPlan)
async def generate_learning_plan(
    current_user: User = Depends(get_current_active_user),
    advisor_service: AdvisorService = Depends(get_advisor_service)
):
    return await advisor_service.generate_learning_plan(current_user)
