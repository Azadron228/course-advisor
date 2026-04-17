from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import CourseORM
from ..dtos.course import CourseDTO
import json

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[CourseDTO]:
        orms = self.db.scalars(select(CourseORM)).all()
        courses = []
        for o in orms:
            skills = o.skills_taught
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except json.JSONDecodeError:
                    skills = []
            if not isinstance(skills, list):
                skills = []
                
            courses.append(CourseDTO(
                id=o.id,
                subject_name=o.subject_name,
                credits=o.credits,
                description=o.description,
                skills_taught=skills,
                difficulty=o.difficulty if o.difficulty is not None else 0.0,
                workload=o.workload if o.workload is not None else 0.0,
                prerequisites=[],
                materials_content=o.materials_content
            ))
        return courses

    def get_orm_by_id(self, course_id: str) -> CourseORM | None:
        return self.db.scalar(select(CourseORM).where(CourseORM.id == course_id))

    def save(self, course: CourseORM) -> CourseORM:
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: CourseORM) -> None:
        self.db.delete(course)
        self.db.commit()
