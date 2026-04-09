from backend.models import Student, Course, UserPreference

class PreferenceScorer:
    def score(self, student: Student, course: Course, preference: UserPreference) -> float:
        # 1. Check interest tags overlap
        interest_match = 0.0
        course_text = (course.subject_name + " " + course.description).lower()
        
        matches = 0
        for tag in preference.interest_tags:
            if tag.lower() in course_text:
                matches += 1
        
        if preference.interest_tags:
            interest_match = matches / len(preference.interest_tags)
            
        # 2. Penalize for exceeding max workload or target difficulty
        # Heuristic: 1.0 if within limits, reduced if outside
        penalty = 1.0
        if course.difficulty > preference.target_difficulty:
            penalty *= (1.0 - (course.difficulty - preference.target_difficulty))
        if course.workload > preference.max_workload:
            penalty *= (1.0 - (course.workload - preference.max_workload))
            
        return interest_match * max(0.0, penalty)
