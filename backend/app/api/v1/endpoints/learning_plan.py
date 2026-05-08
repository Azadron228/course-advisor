from fastapi import APIRouter, Depends, HTTPException, Body
from app.api.deps import get_current_active_user, get_learning_plan_service, get_arq_pool
from app.domain.identity.entities import User
from app.services.learning_plan_service import LearningPlanService
from app.api.v1.schemas.recommendations import (
    LearningPlan,
    PlanGenerateRequest,
    LearningPlanSummary,
    LearningPlanDetail,
    LessonDetail,
)
from typing import Dict, List

router = APIRouter()


@router.get("/", response_model=List[LearningPlanSummary])
async def list_learning_plans(
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    return service.list_plans(current_user.id)


@router.get("/{plan_id}", response_model=LearningPlanDetail)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
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
    service: LearningPlanService = Depends(get_learning_plan_service),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")

    deleted = service.delete_plan(current_user.id, plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Learning plan not found")

    return None


@router.get("/{plan_id}/lessons/{step_order}", response_model=LessonDetail)
async def get_step_detail(
    plan_id: int,
    step_order: int,
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
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
    arq_pool=Depends(get_arq_pool),
):
    return await service.generate_plan(current_user, request, arq_pool)


@router.patch("/{plan_id}/lessons/{step_order}", response_model=LearningPlan)
async def update_learning_plan_step(
    plan_id: int,
    step_order: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    service: LearningPlanService = Depends(get_learning_plan_service),
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
