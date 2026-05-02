from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CourseMaterial:
    id: int
    course_id: int
    filename: str
    content: str
    status: str
    created_at: str
    total_chunks: int = 0
    processed_chunks: int = 0


@dataclass
class CourseMaterialChunk:
    id: Optional[int]
    material_id: int
    content: str
    embedding: List[float]
    chunk_index: int


@dataclass
class Course:
    id: int
    subject_name: str
    description: str
    skills_taught: List[str]
    materials: List[CourseMaterial] = field(default_factory=list)
    embedding: Optional[List[float]] = field(default_factory=list)
