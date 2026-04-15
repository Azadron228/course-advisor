from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

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

Course = CoursePublic

class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float = Field(ge=0, le=100)

class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]

class UserPreference(BaseModel):
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float
