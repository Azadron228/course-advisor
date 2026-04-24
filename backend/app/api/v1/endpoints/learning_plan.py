from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api.deps import get_current_active_user
from app.api.v1.schemas.auth import UserPublic as User

router = APIRouter()

class PlanStep(BaseModel):
    title: str
    description: str
    status: str # 'completed', 'current', 'upcoming'

class LearningPlanResponse(BaseModel):
    career_goal: str
    steps: List[PlanStep]

@router.get("/", response_model=LearningPlanResponse)
async def get_learning_plan(current_user: User = Depends(get_current_active_user)):
    steps = [
        PlanStep(title="Intro to Python", description="Master basic syntax", status="completed"),
        PlanStep(title="Data Structures", description="Learn lists, dicts, sets", status="current"),
        PlanStep(title="Machine Learning", description="Build first model", status="upcoming"),
    ]
    return LearningPlanResponse(career_goal="AI Engineer", steps=steps)
