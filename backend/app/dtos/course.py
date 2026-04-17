from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TranscriptEntryDTO:
    subject_name: str
    credits: float
    mark: float

@dataclass
class StudentDTO:
    id: str
    name: str
    transcript: List[TranscriptEntryDTO]
    current_skills: List[str]

@dataclass
class UserPreferenceDTO:
    interest_tags: List[str]
    target_difficulty: float
    max_workload: float

@dataclass
class CourseDTO:
    id: str
    subject_name: str
    credits: float
    description: str
    skills_taught: List[str]
    difficulty: float
    workload: float
    materials_content: Optional[str] = None
    prerequisites: Optional[List[str]] = None

@dataclass
class CourseCreateDTO:
    id: str
    subject_name: str
    credits: float
    description: str
    skills_taught: List[str]
    difficulty: float
    workload: float
    materials_content: Optional[str] = None
