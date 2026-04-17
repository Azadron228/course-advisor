from dataclasses import dataclass
from typing import Optional

@dataclass
class UserDTO:
    email: str
    hashed_password: str
    id: Optional[int] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = False
