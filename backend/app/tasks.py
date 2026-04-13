import asyncio
from .models import Student, Course, ModelProvider
from .agent import recommendation_agent, get_model, AgentDeps, is_capable_model, parse_agent_recommendation, AgentRecommendation

# Task to run the agent
def run_agent_task(student_dict, course_dict, provider_name):
    student = Student(**student_dict)
    course = Course(**course_dict)
    provider = ModelProvider(provider_name)
    
    async def _run():
        model = get_model(provider)
        deps = AgentDeps(student=student, course=course)
        capable = is_capable_model(model)
        
        if capable:
            result = await recommendation_agent.run(
                "Evaluate how well this course fits the student.",
                model=model,
                deps=deps,
                output_type=AgentRecommendation
            )
            return result.output.model_dump()
        else:
            prompt = (
                "Evaluate how well this course fits the student.\n\n"
                "Output MUST be ONLY a valid JSON object with the following structure:\n"
                "{\n"
                "  \"score\": 0.85,\n"
                "  \"reasoning\": \"Detailed explanation here...\",\n"
                "  \"tags\": [\"Tag 1\", \"Tag 2\"]\n"
                "}"
            )
            result = await recommendation_agent.run(
                prompt,
                model=model,
                deps=deps,
                output_type=str
            )
            return parse_agent_recommendation(result.output).model_dump()

    return asyncio.run(_run())
