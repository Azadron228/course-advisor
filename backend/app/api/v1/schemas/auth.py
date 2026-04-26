from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool
    disabled: Optional[bool] = None
    career_goal: Optional[str] = None
    onboarding_completed: bool = False
    is_active: bool = True
    interests: Optional[List[str]] = None
    default_skill_level: Optional[str] = None
    default_learning_style: Optional[str] = None
    default_study_time: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    disabled: Optional[bool] = None
    career_goal: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    interests: Optional[List[str]] = None
    default_skill_level: Optional[str] = None
    default_learning_style: Optional[str] = None
    default_study_time: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
