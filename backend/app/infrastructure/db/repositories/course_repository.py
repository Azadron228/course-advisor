from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.infrastructure.db.models import CourseORM, CourseMaterialORM, CourseMaterialChunkORM
from app.domain.catalog.entities import Course, CourseMaterial, CourseMaterialChunk
import json


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_content_similarity(self, course_id: int, embedding: list[float]) -> float:
        # 1 - cosine_distance is the standard similarity in pgvector
        query = select(1 - CourseORM.embedding.cosine_distance(embedding)).where(
            CourseORM.id == course_id
        )
        result = self.db.scalar(query)
        return float(result) if result is not None else 0.0

    def get_all(self) -> list[Course]:
        orms = self.db.scalars(select(CourseORM)).all()
        courses = []
        for o in orms:
            courses.append(self._to_entity(o))
        return courses

    def get_by_id(self, course_id: int) -> Course | None:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if not o:
            return None
        return self._to_entity(o)

    def _to_entity(self, o: CourseORM) -> Course:
        skills = o.skills_taught
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                skills = []
        
        if not isinstance(skills, list):
            skills = []

        materials = []
        for m in o.materials:
            materials.append(
                CourseMaterial(
                    id=m.id,
                    course_id=m.course_id,
                    filename=m.filename,
                    content=m.content,
                    status=m.status,
                    total_chunks=m.total_chunks,
                    processed_chunks=m.processed_chunks,
                    created_at=m.created_at.isoformat(),
                )
            )

        return Course(
            id=o.id,
            subject_name=o.subject_name,
            description=o.description,
            skills_taught=skills,
            materials=materials,
            embedding=list(o.embedding) if o.embedding is not None else [],
        )

    def save(self, course: Course) -> Course:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course.id))
        if not o:
            o = CourseORM()  # ID is autoincremented
            self.db.add(o)

        o.subject_name = course.subject_name
        o.description = course.description
        setattr(o, "skills_taught", course.skills_taught)
        o.embedding = course.embedding

        self.db.commit()
        self.db.refresh(o)

        return self._to_entity(o)

    def delete(self, course_id: int) -> None:
        o = self.db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if o:
            self.db.delete(o)
            self.db.commit()

    # Materials management
    def add_material(self, material: CourseMaterial) -> CourseMaterial:
        m_orm = CourseMaterialORM(
            course_id=material.course_id,
            filename=material.filename,
            content=material.content,
            status=material.status,
        )
        self.db.add(m_orm)
        self.db.commit()
        self.db.refresh(m_orm)
        
        material.id = m_orm.id
        material.created_at = m_orm.created_at.isoformat()
        return material

    def delete_material(self, material_id: int) -> None:
        m_orm = self.db.get(CourseMaterialORM, material_id)
        if m_orm:
            self.db.delete(m_orm)
            self.db.commit()

    def get_material(self, material_id: int) -> CourseMaterial | None:
        m = self.db.get(CourseMaterialORM, material_id)
        if not m:
            return None
        return CourseMaterial(
            id=m.id,
            course_id=m.course_id,
            filename=m.filename,
            content=m.content,
            status=m.status,
            total_chunks=m.total_chunks,
            processed_chunks=m.processed_chunks,
            created_at=m.created_at.isoformat(),
        )

    def add_material_chunks(self, chunks: list[CourseMaterialChunk]) -> None:
        for chunk in chunks:
            orm = CourseMaterialChunkORM(
                material_id=chunk.material_id,
                content=chunk.content,
                embedding=chunk.embedding,
                chunk_index=chunk.chunk_index
            )
            self.db.add(orm)
        self.db.commit()

    def get_best_material_similarity(self, course_id: int, student_embedding: list[float]) -> float:
        """Finds the maximum similarity score among all chunks of a course."""
        query = (
            select(func.max(1 - CourseMaterialChunkORM.embedding.cosine_distance(student_embedding)))
            .join(CourseMaterialORM)
            .where(CourseMaterialORM.course_id == course_id)
        )
        result = self.db.scalar(query)
        return float(result) if result is not None else 0.0
