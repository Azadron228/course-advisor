from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import get_current_active_user
from app.api.v1.schemas.auth import UserPublic as User
from app.api.v1.schemas.recommendations import SkillMapResponse, SkillNode

router = APIRouter()

@router.get("/map", response_model=SkillMapResponse)
async def get_skill_map(current_user: User = Depends(get_current_active_user)):
    # Mock data for the prototype skill map
    nodes = [
        SkillNode(id="ml1", label="Machine Learning Basics", mastery_level=80, category="AI"),
        SkillNode(id="web1", label="Frontend Development", mastery_level=40, category="Engineering"),
        SkillNode(id="data1", label="Data Structures", mastery_level=90, category="Computer Science")
    ]
    return SkillMapResponse(nodes=nodes)
