from pydantic import BaseModel, Field
from typing import List, Optional

class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float = Field(ge=0, le=100)

class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]

class Course(BaseModel):
    id: str
    subject_name: str
    credits: float
    description: str
    prerequisites: List[str]
    skills_taught: List[str]
    difficulty: float = Field(ge=0, le=1)
    workload: float = Field(ge=0, le=1)
