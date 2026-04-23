from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Course:
    id: str
    subject_name: str
    credits: float
    description: str
    skills_taught: Dict
    difficulty: float
    workload: float
    materials_content: Optional[str] = None
    embedding: Optional[List[float]] = field(default_factory=list)
