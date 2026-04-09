from backend.db import get_connection
from backend.embeddings import get_embedding
from backend.models import Student

class ContentScorer:
    def score(self, student: Student, course_id: str) -> float:
        # 1. Aggregate transcript subject names
        # In a more advanced version we'd use credits to weight these
        subjects = [entry.subject_name for entry in student.transcript]
        if not subjects:
             return 0.0
             
        aggregated_text = " ".join(subjects)
        
        # 2. Get embedding for the aggregated text
        vector = get_embedding(aggregated_text)
        
        # 3. Query pgvector for cosine similarity to course.embedding
        # PostgreSQL <=> is cosine distance, so 1 - distance = similarity
        with get_connection() as conn:
            with conn.cursor() as cur:
                # We need to register vector on every cursor if using pgvector-python
                from pgvector.psycopg import register_vector
                register_vector(cur)
                
                cur.execute(
                    "SELECT 1 - (embedding <=> %s) AS score FROM courses WHERE id = %s",
                    (vector, course_id)
                )
                result = cur.fetchone()
                if result:
                    return float(result[0])
        return 0.0
