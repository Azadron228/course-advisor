import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from arq.jobs import Job, JobStatus

from .schemas.recommendations import (
    Student, UserPreference,
    RecommendationResponse,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ModelProvider
)
from .schemas.auth import UserPublic as User
from ...repositories.course import CourseRepository
from ...scoring.orchestrator import HybridScorer
from ...core.redis_chat import RedisChatHistory
from llama_index.core.base.llms.types import ChatMessage as LLMChatMessage, MessageRole
from ...agent import get_advisor_agent, get_model
from ..deps import get_db, get_current_active_user, get_arq_pool

logger = logging.getLogger(__name__)

router = APIRouter()
scorer = HybridScorer()
chat_history = RedisChatHistory()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Get history from Redis
        history_dicts = await chat_history.get_history(current_user.email)
        
        # Convert to LlamaIndex ChatMessage format
        chat_messages = []
        for m in history_dicts:
            role = MessageRole.USER if m["role"] == "user" else MessageRole.ASSISTANT
            chat_messages.append(LLMChatMessage(role=role, content=m["content"]))
        
        # Get the agent
        llm = get_model(ModelProvider.AUTO)
        # For now, we use defaults for transcript/skills or we could fetch from DB if available
        # Assuming for this task we use placeholders or what we have.
        # In a real scenario, we'd fetch the student record.
        agent = get_advisor_agent(llm)
        
        # Chat with agent
        logger.info(f"Chat request from user {current_user.email}: {request.message[:50]}...")
        response = await agent.run(user_msg=request.message, chat_history=chat_messages)
        response_content = str(response)
        
        # Store new messages
        await chat_history.add_message(current_user.email, "user", request.message)
        await chat_history.add_message(current_user.email, "assistant", response_content)
        
        # Return updated history
        updated_history_dicts = await chat_history.get_history(current_user.email)
        history = [ChatMessage(**m) for m in updated_history_dicts]
        
        return ChatResponse(response=response_content, history=history)
    except Exception as e:
        logger.error(f"Error in chat_with_advisor for user {current_user.email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")


@router.get("/chat/history", response_model=List[ChatMessage])
async def get_chat_history_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    history_dicts = await chat_history.get_history(current_user.email)
    return [ChatMessage(**m) for m in history_dicts]


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    course_repo = CourseRepository(db)
    courses = course_repo.get_all()
    if not courses:
         return RecommendationResponse(results=[])
    return await scorer.recommend(db, student, courses, preference, provider=ModelProvider.AUTO)


@router.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: Student,
    preference: UserPreference,
    arq_pool = Depends(get_arq_pool),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    course_repo = CourseRepository(db)
    courses = course_repo.get_all()
    job = await arq_pool.enqueue_job(
        'run_hybrid_recommendation',
        student.model_dump(),
        [c.__dict__ for c in courses],
        preference.model_dump()
    )
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to enqueue job")
    return {"job_id": job.job_id}


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    arq_pool = Depends(get_arq_pool),
    current_user: User = Depends(get_current_active_user)
):
    job = Job(job_id, arq_pool)
    try:
        status_val = await job.status()
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if status_val == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")
        
    info = await job.info()
    return {
        "job_id": job.job_id,
        "status": status_val.value if hasattr(status_val, 'value') else str(status_val),
        "result": await job.result(timeout=0) if status_val == JobStatus.complete else None,
        "enqueued_at": info.enqueue_time if info else None,
        "started_at": info.start_time if info else None,
        "ended_at": None
    }
