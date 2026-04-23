from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    email: str
    full_name: Optional[str]
    disabled: bool = False
    is_admin: bool = False
    hashed_password: Optional[str] = None
