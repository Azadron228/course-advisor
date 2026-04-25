from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user, get_service
from app.domain.identity.entities import User
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.api.v1.schemas.dashboard import DashboardResponse

router = APIRouter()

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    active_plan = plan_repo.get_active_plan(current_user.id)
    
    active_plan_title = active_plan.goal if active_plan else None
    
    # Mock progress for now
    progress = 0
    if active_plan and active_plan.steps:
        # In a real implementation we would check completed steps
        progress = 0 

    welcome_message = f"Welcome back, {current_user.full_name or 'Student'}!"
    
    return DashboardResponse(
        active_plan_title=active_plan_title,
        progress_percentage=progress,
        welcome_message=welcome_message,
        onboarding_completed=current_user.onboarding_completed
    )
