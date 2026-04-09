from backend.agent import recommendation_agent, AgentRecommendation
from backend.models import Student, Course

class RAGScorer:
    async def score(self, student: Student, course: Course) -> AgentRecommendation:
        # Construct the prompt
        transcript_summary = ", ".join([e.subject_name for e in student.transcript])
        current_skills = ", ".join(student.current_skills)
        course_skills = ", ".join(course.skills_taught)
        
        user_prompt = (
            f"Student Transcript: {transcript_summary}\n"
            f"Student Current Skills: {current_skills}\n"
            f"Course: {course.subject_name}\n"
            f"Course Description: {course.description}\n"
            f"Skills Taught in Course: {course_skills}\n"
            "Evaluate how well this course fits the student."
        )
        
        result = await recommendation_agent.run(user_prompt, result_type=AgentRecommendation)
        return result.data
