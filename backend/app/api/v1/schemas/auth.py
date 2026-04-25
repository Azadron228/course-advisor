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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
