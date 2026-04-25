from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user, get_advisor_service
from app.domain.identity.entities import User
from app.api.v1.schemas.recommendations import SkillMapResponse
from app.services.advisor_service import AdvisorService

router = APIRouter()

@router.get("/map", response_model=SkillMapResponse)
async def get_skill_map(
    current_user: User = Depends(get_current_active_user),
    advisor_service: AdvisorService = Depends(get_advisor_service)
):
    return advisor_service.get_skill_map(current_user.id)
