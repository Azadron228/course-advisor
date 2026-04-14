from .schemas.course import Student, Course, UserPreference
from .scoring.orchestrator import HybridScorer
from .db import SessionLocal

async def run_hybrid_recommendation(ctx: dict, student_dict: dict, courses_list: list, preference_dict: dict) -> dict:
    student = Student(**student_dict)
    courses = [Course(**c) for c in courses_list]
    preference = UserPreference(**preference_dict)
    
    scorer = HybridScorer()
    
    db = SessionLocal()
    try:
        response = await scorer.recommend(db, student, courses, preference)
        return response.model_dump()
    finally:
        db.close()
