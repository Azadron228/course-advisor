from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from enum import Enum


class ModelProvider(str, Enum):
    AUTO = "auto"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class CourseMaterialPublic(BaseModel):
    id: int
    course_id: int
    filename: str
    status: str
    total_chunks: int = 0
    processed_chunks: int = 0
    created_at: str
    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    subject_name: str
    description: str
    skills_taught: List[str]


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    subject_name: Optional[str] = None
    description: Optional[str] = None
    skills_taught: Optional[List[str]] = None


class CoursePublic(CourseBase):
    id: int
    materials: List[CourseMaterialPublic] = []
    model_config = ConfigDict(from_attributes=True)


class Course(CoursePublic):
    pass
