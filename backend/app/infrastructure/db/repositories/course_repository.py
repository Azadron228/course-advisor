from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.infrastructure.db.models import CourseORM
from app.domain.catalog.entities import Course
import json

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_content_similarity(self, course_id: str, embedding: list[float]) -> float:
        # 1 - cosine_distance is the standard similarity in pgvector
        query = select(1 - CourseORM.embedding.cosine_distance(embedding)).where(CourseORM.id == course_id)
        result = self.db.scalar(query)
        return float(result) if result is not None else 0.0


    def get_all(self) -> list[Course]:
        orms = self.db.scalars(select(CourseORM)).all()
        courses = []
        for o in orms:
            skills = o.skills_taught
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except json.JSONDecodeError:
                    skills = {}
            
            courses.append(Course(
                id=o.id,
                subject_name=o.subject_name,
                credits=o.credits,
                description=o.description,
                skills_taught=skills,
                difficulty=o.difficulty if o.difficulty is not None else 0.0,
                workload=o.workload if o.workload is not None else 0.0,
                materials_content=o.materials_content,
                embedding=list(o.embedding) if o.embedding is not None else []
            ))
        return courses

    def get_by_id(self, course_id: str) -> Course | None:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if not o:
            return None
            
        skills = o.skills_taught
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                skills = {}
                
        return Course(
            id=o.id,
            subject_name=o.subject_name,
            credits=o.credits,
            description=o.description,
            skills_taught=skills,
            difficulty=o.difficulty if o.difficulty is not None else 0.0,
            workload=o.workload if o.workload is not None else 0.0,
            materials_content=o.materials_content,
            embedding=list(o.embedding) if o.embedding is not None else []
        )

    def save(self, course: Course) -> Course:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course.id))
        if not o:
            o = CourseORM(id=course.id)
            self.db.add(o)
        
        o.subject_name = course.subject_name
        o.credits = course.credits
        o.description = course.description
        o.skills_taught = course.skills_taught
        o.difficulty = course.difficulty
        o.workload = course.workload
        o.materials_content = course.materials_content
        o.embedding = course.embedding
        
        self.db.commit()
        self.db.refresh(o)
        return course

    def delete(self, course_id: str) -> None:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if o:
            self.db.delete(o)
            self.db.commit()
