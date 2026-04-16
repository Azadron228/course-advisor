import logging
from .schemas.course import Student, Course, UserPreference
from .scoring.orchestrator import HybridScorer
from .db import SessionLocal

logger = logging.getLogger(__name__)

async def run_hybrid_recommendation(ctx: dict, student_dict: dict, courses_list: list, preference_dict: dict) -> dict:
    try:
        student = Student(**student_dict)
        courses = [Course(**c) for c in courses_list]
        preference = UserPreference(**preference_dict)
        
        scorer = HybridScorer()
        
        db = SessionLocal()
        try:
            response = await scorer.recommend(db, student, courses, preference)
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error in hybrid recommendation logic: {e}", exc_info=True)
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "status": "failed"
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in run_hybrid_recommendation task: {e}", exc_info=True)
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "failed"
        }
