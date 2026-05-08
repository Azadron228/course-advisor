from dataclasses import dataclass


@dataclass
class PracticeTest:
    id: int
    lesson_id: int
    content: dict
    created_at: str


@dataclass
class UserTestScore:
    id: int
    user_id: int
    lesson_id: int
    score: int
    attempts: int
    completed_at: str
