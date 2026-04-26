from fastapi import APIRouter, Depends, HTTPException, Body
from app.api.deps import get_current_active_user, get_advisor_service, get_service
from app.domain.identity.entities import User
from app.services.advisor_service import AdvisorService
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.api.v1.schemas.recommendations import LearningPlan
from typing import Dict, List, Optional

router = APIRouter()

@router.get("/", response_model=List[LearningPlan])
async def list_learning_plans(
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    return plan_repo.get_all_plans(current_user.id)

@router.get("/{plan_id}", response_model=LearningPlan)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    plan = plan_repo.get_by_id(current_user.id, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.post("/generate", response_model=LearningPlan)
async def generate_learning_plan(
    current_user: User = Depends(get_current_active_user),
    advisor_service: AdvisorService = Depends(get_advisor_service)
):
    return await advisor_service.generate_learning_plan(current_user)

@router.patch("/steps/{step_order}", response_model=LearningPlan)
async def update_learning_plan_step(
    step_order: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    plan = plan_repo.get_active_plan(current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active learning plan found")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    # Update the specific step status
    updated_steps = []
    found = False
    for step in plan.steps:
        if step.order == step_order:
            # Create updated step
            from dataclasses import replace
            updated_step = replace(step, status=new_status)
            updated_steps.append(updated_step)
            found = True
        else:
            updated_steps.append(step)
            
    if not found:
        raise HTTPException(status_code=404, detail="Step not found")
        
    from dataclasses import replace
    updated_plan = replace(plan, steps=updated_steps)
    
    return plan_repo.update_plan(current_user.id, updated_plan)
