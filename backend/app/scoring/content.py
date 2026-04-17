import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..api.v1.schemas.recommendations import Student
from ..models import CourseORM
from ..embeddings import get_embedding

logger = logging.getLogger(__name__)

class ContentScorer:
    def score(self, db: Session, student: Student, course_id: str) -> float:
        # 1. Aggregate transcript subject names
        subjects = [entry.subject_name for entry in student.transcript]
        if not subjects:
             logger.warning(f"No transcript subjects for student {student.id}")
             return 0.0
             
        aggregated_text = " ".join(subjects)
        
        # 2. Get embedding for the aggregated text
        vector = get_embedding(aggregated_text)
        
        # 3. Query pgvector for cosine similarity to course.embedding using SQLAlchemy
        course = db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if course is not None and course.embedding is not None:
            # 1 - cosine_distance is the standard similarity in pgvector
            query = select(1 - CourseORM.embedding.cosine_distance(vector)).where(CourseORM.id == course_id)
            result = db.scalar(query)
            if result is not None:
                score = float(result)
                if score == 0.0:
                     logger.warning(f"Content similarity score is 0.0 for course {course_id}. Check if embeddings are zero-vectors.")
                return score
            
        logger.warning(f"No result found or embedding is NULL for course {course_id} in database.")
        return 0.0
