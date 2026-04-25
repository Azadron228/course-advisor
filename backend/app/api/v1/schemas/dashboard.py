from pydantic import BaseModel
from typing import Optional

class DashboardResponse(BaseModel):
    active_plan_title: Optional[str] = None
    progress_percentage: int = 0
    welcome_message: str
    onboarding_completed: bool
