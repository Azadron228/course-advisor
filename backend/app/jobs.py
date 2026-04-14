import asyncio
import os
import redis
from rq import Queue
from .schemas.course import Student, Course, UserPreference
from .scoring.orchestrator import HybridScorer
from .db import SessionLocal

# Redis for workers
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)

# Task to run the hybrid recommendation process
def run_hybrid_recommendation(student_dict, courses_list, preference_dict):
    student = Student(**student_dict)
    courses = [Course(**c) for c in courses_list]
    preference = UserPreference(**preference_dict)
    
    scorer = HybridScorer()
    
    async def _run():
        db = SessionLocal()
        try:
            response = await scorer.recommend(db, student, courses, preference)
            return response.model_dump()
        finally:
            db.close()
        
    return asyncio.run(_run())
