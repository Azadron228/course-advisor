from dataclasses import dataclass
from typing import Optional, List


@dataclass
class User:
    id: Optional[int]
    email: str
    full_name: Optional[str]
    disabled: bool = False
    is_admin: bool = False
    hashed_password: Optional[str] = None
    career_goal: Optional[str] = None
    onboarding_completed: bool = False
    interests: Optional[List[str]] = None
    default_skill_level: Optional[str] = None
    default_learning_style: Optional[str] = None
    default_study_time: Optional[int] = 10
