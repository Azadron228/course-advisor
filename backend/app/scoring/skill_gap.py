from sqlalchemy.orm import Session
from ..schemas.course import Student, CoursePublic as Course

class SkillGapScorer:
    def score(self, db: Session, student: Student, course: Course) -> float:
        taught = set(course.skills_taught)
        current = set(student.current_skills)
        if not taught:
             return 0.0
        new_skills = taught - current
        return len(new_skills) / len(taught)
