import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.schemas.recommendations import (
    Student as StudentSchema,
    UserPreference as UserPreferenceSchema,
    RecommendationResponse as RecommendationResponseSchema,
    ChatRequest,
    ChatResponse,
    ChatMessage,
)
from app.domain.recommendation.entities import (
    Student,
    UserPreference,
    TranscriptEntry,
    ModelProvider as DomainModelProvider,
)
from app.api.v1.schemas.auth import UserPublic as User
from app.services.advisor_service import AdvisorService
from app.infrastructure.cache.redis_chat import RedisChatHistory
from llama_index.core.base.llms.types import ChatMessage as LLMChatMessage, MessageRole
from app.infrastructure.ai.agent import get_advisor_agent, get_model
from app.api.deps import (
    get_current_active_user,
    get_arq_pool,
    get_advisor_service,
    get_chat_history_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    chat_history: RedisChatHistory = Depends(get_chat_history_service),
):
    try:
        history_dicts = await chat_history.get_history(current_user.email)

        chat_messages = []
        for m in history_dicts:
            role = MessageRole.USER if m["role"] == "user" else MessageRole.ASSISTANT
            chat_messages.append(LLMChatMessage(role=role, content=m["content"]))

        llm = get_model(DomainModelProvider.AUTO)
        agent = get_advisor_agent(llm)

        logger.info(f"Chat request from user {current_user.email}: {request.message[:50]}...")
        response = await agent.run(user_msg=request.message, chat_history=chat_messages)
        response_content = str(response)

        await chat_history.add_message(current_user.email, "user", request.message)
        await chat_history.add_message(current_user.email, "assistant", response_content)

        updated_history_dicts = await chat_history.get_history(current_user.email)
        history = [ChatMessage(**m) for m in updated_history_dicts]

        return ChatResponse(response=response_content, history=history)
    except Exception as e:
        logger.error(
            f"Error in chat_with_advisor for user {current_user.email}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")


@router.get("/chat/history", response_model=List[ChatMessage])
async def get_chat_history_endpoint(
    current_user: User = Depends(get_current_active_user),
    chat_history: RedisChatHistory = Depends(get_chat_history_service),
):
    history_dicts = await chat_history.get_history(current_user.email)
    return [ChatMessage(**m) for m in history_dicts]


@router.post("/recommend", response_model=RecommendationResponseSchema)
async def get_recommendations(
    student_schema: StudentSchema,
    preference_schema: UserPreferenceSchema,
    advisor_service: AdvisorService = Depends(get_advisor_service),
    current_user: User = Depends(get_current_active_user),
):
    # Convert Schemas to Domain Entities
    transcript = [TranscriptEntry(**entry.model_dump()) for entry in student_schema.transcript]
    student = Student(
        id=student_schema.id,
        name=student_schema.name,
        transcript=transcript,
        current_skills=student_schema.current_skills,
    )
    preference = UserPreference(
        interest_tags=preference_schema.interest_tags,
        target_difficulty=preference_schema.target_difficulty,
        max_workload=preference_schema.max_workload,
    )

    # We still need all courses for recommendation
    courses = advisor_service.course_repo.get_all()
    if not courses:
        return RecommendationResponseSchema(results=[])

    domain_response = await advisor_service.recommend(
        student, courses, preference, provider=DomainModelProvider.AUTO
    )

    # Return domain response (FastAPI will convert dataclass to schema)
    return domain_response


@router.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: StudentSchema,
    preference: UserPreferenceSchema,
    arq_pool=Depends(get_arq_pool),
    current_user: User = Depends(get_current_active_user),
):
    job = await arq_pool.enqueue_job(
        "run_hybrid_recommendation",
        student.model_dump(),
        preference.model_dump(),
        "auto",
    )
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue job")
    return {"job_id": job.job_id}
