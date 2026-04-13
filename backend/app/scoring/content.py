import logging
from ..db import get_connection
from ..embeddings import get_embedding
from ..models import Student

logger = logging.getLogger(__name__)

class ContentScorer:
    def score(self, student: Student, course_id: str) -> float:
        # 1. Aggregate transcript subject names
        subjects = [entry.subject_name for entry in student.transcript]
        if not subjects:
             logger.warning(f"No transcript subjects for student {student.id}")
             return 0.0
             
        aggregated_text = " ".join(subjects)
        
        # 2. Get embedding for the aggregated text
        vector = get_embedding(aggregated_text)
        
        # 3. Query pgvector for cosine similarity to course.embedding
        with get_connection() as conn:
            from pgvector.psycopg2 import register_vector
            register_vector(conn)
            
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 - (embedding <=> %s::vector) AS score, embedding IS NULL as is_null FROM courses WHERE id = %s",
                    (vector, course_id)
                )
                result = cur.fetchone()
                if result:
                    score = float(result[0])
                    is_null = result[1]
                    if is_null:
                        logger.warning(f"Embedding is NULL for course {course_id}")
                    if score == 0.0:
                         logger.warning(f"Content similarity score is 0.0 for course {course_id}. Check if embeddings are zero-vectors.")
                    return score
        logger.warning(f"No result found for course {course_id} in database.")
        return 0.0
