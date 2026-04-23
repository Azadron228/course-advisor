from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum


class ModelProvider(str, Enum):
    AUTO = "auto"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class CourseBase(BaseModel):
    id: str
    subject_name: str
    credits: float
    description: str
    skills_taught: List[str]
    difficulty: float = Field(ge=0, le=1)
    workload: float = Field(ge=0, le=1)
    materials_content: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CoursePublic(CourseBase):
    model_config = ConfigDict(from_attributes=True)


class Course(CoursePublic):
    pass
