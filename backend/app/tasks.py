import asyncio
from .schemas.course import Student, CoursePublic as Course
from .schemas.internal import ModelProvider
from .agent import get_recommendation_agent, get_model, parse_agent_recommendation, AgentRecommendation

async def run_agent_task(ctx: dict, student_dict: dict, course_dict: dict, provider_name: str) -> dict:
    student = Student(**student_dict)
    course = Course(**course_dict)
    provider = ModelProvider(provider_name)
    
    llm = get_model(provider)
    agent = get_recommendation_agent(llm, student, course)
    
    # In LlamaIndex 0.14.x, we use agent.run(user_msg=...)
    # We ask it to evaluate and provide the JSON output as specified in its system prompt
    response = await agent.run(user_msg="Evaluate how well this course fits the student and provide your recommendation in JSON format.")
    
    # response is an AgentOutput object, str(response) returns response.response.content
    return parse_agent_recommendation(str(response)).model_dump()
