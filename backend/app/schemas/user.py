from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    hashed_password: str
