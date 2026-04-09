from backend.models import Student, Course

class SkillGapScorer:
    def score(self, student: Student, course: Course) -> float:
        taught = set(course.skills_taught)
        current = set(student.current_skills)
        if not taught:
             return 0.0
        new_skills = taught - current
        return len(new_skills) / len(taught)
