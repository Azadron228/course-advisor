from app.domain.recommendation.entities import Student, UserPreference
from app.domain.catalog.entities import Course


class ScoringService:
    def calculate_skill_gap(self, student: Student, course: Course) -> float:
        taught = set(course.skills_taught)
        current = set(student.current_skills)
        if not taught:
            return 0.0
        new_skills = taught - current
        return len(new_skills) / len(taught)

    def calculate_preference_score(self, course: Course, preference: UserPreference) -> float:
        # Simplified preference scoring logic
        if not preference.interest_tags:
            return 0.5

        tags = set(preference.interest_tags)
        # Check against course description or subject name or skills
        course_text = (
            f"{course.subject_name} {course.description} {' '.join(course.skills_taught)}".lower()
        )
        matches = sum(1 for tag in tags if tag.lower() in course_text)

        pref_score = matches / len(tags) if tags else 0.5

        # Factor in difficulty and workload
        diff_penalty = abs(course.difficulty - preference.target_difficulty)
        work_penalty = max(0, course.workload - preference.max_workload)

        return max(0, pref_score - (diff_penalty * 0.2) - (work_penalty * 0.2))

    def combine_scores(
        self,
        content_sim: float,
        skill_gap: float,
        rag_score: float,
        pref_score: float,
        course: Course,
    ) -> float:
        return (content_sim * 0.3) + (skill_gap * 0.3) + (rag_score * 0.2) + (pref_score * 0.2)
