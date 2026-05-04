import logging
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.v1.schemas.recommendations import (
    Student as StudentSchema,
    UserPreference as UserPreferenceSchema,
    RecommendationResponse as RecommendationResponseSchema,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatSession as ChatSessionSchema,
    ChatSessionDetail as ChatSessionDetailSchema,
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
from app.infrastructure.db.repositories.chat_repository import ChatRepository
from llama_index.core.base.llms.types import ChatMessage as LLMChatMessage, MessageRole
from llama_index.core.agent.workflow.workflow_events import AgentStream, AgentOutput
from app.infrastructure.ai.agent import get_advisor_agent, get_model
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from sqlalchemy.orm import Session
from app.api.deps import (
    get_current_active_user,
    get_arq_pool,
    get_advisor_service,
    get_chat_history_service,
    get_chat_repository,
    get_db,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/chat/sessions", response_model=List[ChatSessionSchema])
async def list_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    chat_repo: ChatRepository = Depends(get_chat_repository),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    return chat_repo.list_sessions(current_user.id)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionDetailSchema)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    chat_repo: ChatRepository = Depends(get_chat_repository),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    session = chat_repo.get_session(current_user.id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    chat_repo: ChatRepository = Depends(get_chat_repository),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    chat_repo.delete_session(current_user.id, session_id)
    return {"status": "success"}


@router.post("/chat", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    chat_history: RedisChatHistory = Depends(get_chat_history_service),
    chat_repo: ChatRepository = Depends(get_chat_repository),
    db: Session = Depends(get_db),
):
    try:
        # Retrieve user profile context
        profile_repo = ProfileRepository(db)
        plan_repo = PlanRepository(db)

        skills = profile_repo.get_skills(current_user.id)
        transcript = profile_repo.get_transcript(current_user.id)
        active_plan = plan_repo.get_active_plan(current_user.id)

        # Format context strings
        transcript_summary = (
            ", ".join([f"{e.subject_name} (Credits: {e.credits}, Mark: {e.mark})" for e in transcript])
            if transcript
            else "No transcript available."
        )
        current_skills = (
            ", ".join([f"{s.skill_name} ({s.mastery_level}%)" for s in skills])
            if skills
            else "No skills listed."
        )

        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create a new session with first part of message as title
            title = request.message[:50] + ("..." if len(request.message) > 50 else "")
            session = chat_repo.create_session(current_user.id, title)
            session_id = session.id
            # Also clear redis history for new session
            await chat_history.clear_history(current_user.email)
        
        if session_id is None:
             raise HTTPException(status_code=400, detail="Session ID is required")
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")
        session = chat_repo.get_session(current_user.id, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        # Load history for the agent
        chat_messages = []
        for m in session.messages:
            role = MessageRole.USER if m.role == "user" else MessageRole.ASSISTANT
            chat_messages.append(LLMChatMessage(role=role, content=m.content))

        llm = get_model(DomainModelProvider.AUTO)
        agent = get_advisor_agent(
            llm,
            transcript_summary=transcript_summary,
            current_skills=current_skills,
            user=current_user,
            learning_plan=active_plan,
        )

        logger.info(f"Chat request from user {current_user.email} for session {session_id}: {request.message[:50]}...")

        handler = agent.run(user_msg=request.message, chat_history=chat_messages)

        if request.stream:
            async def stream_generator():
                full_response = ""
                final_answer_started = False
                async for event in handler.stream_events():
                    if isinstance(event, AgentStream):
                        # Skip thinking deltas if supported by the model/agent
                        if getattr(event, "thinking_delta", None):
                            continue

                        delta = event.delta
                        full_response += delta
                        
                        if not final_answer_started:
                            # Use a more robust check for the final answer prefix (start of line or start of string)
                            if re.search(r"(?:^|\n)Final Answer:", full_response):
                                final_answer_started = True
                                # Find the last occurrence to be sure we're at the actual final answer
                                parts = re.split(r"(?:^|\n)Final Answer:", full_response)
                                part = parts[-1].lstrip()
                                if part:
                                    yield part
                        else:
                            yield delta
                
                # If we never detected a final answer prefix but have content, 
                # it might be a direct response without ReAct formatting or 
                # the prefix was missed in the stream.
                if not final_answer_started and full_response:
                    # Still try to clean it up if it somehow has ReAct traces but missed the prefix logic
                    clean_response = full_response
                    if re.search(r"(?:^|\n)Final Answer:", clean_response):
                        clean_response = re.split(r"(?:^|\n)Final Answer:", clean_response)[-1].strip()
                    yield clean_response

                # After streaming finishes, save history (cleaned)
                clean_response = full_response
                if re.search(r"(?:^|\n)Final Answer:", clean_response):
                    clean_response = re.split(r"(?:^|\n)Final Answer:", clean_response)[-1].strip()

                if session_id is None:
                    raise HTTPException(status_code=400, detail="Session ID is required")
                # Save to DB
                chat_repo.add_message(session_id, "user", request.message)
                chat_repo.add_message(session_id, "assistant", clean_response)
                
                # Also save to Redis for quick retrieval of active history
                await chat_history.add_message(current_user.email, "user", request.message)
                await chat_history.add_message(current_user.email, "assistant", clean_response)

            return StreamingResponse(stream_generator(), media_type="text/event-stream")

        result = await handler
        response_content = ""
        if isinstance(result, AgentOutput):
            response_content = str(result.response)
            # Clean up ReAct traces if they leaked into the final response
            if re.search(r"(?:^|\n)Final Answer:", response_content):
                response_content = re.split(r"(?:^|\n)Final Answer:", response_content)[-1].strip()
        else:
            response_content = str(result)

        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID is required")
        # Save to DB
        chat_repo.add_message(session_id, "user", request.message)
        chat_repo.add_message(session_id, "assistant", response_content)

        # Also save to Redis
        await chat_history.add_message(current_user.email, "user", request.message)
        await chat_history.add_message(current_user.email, "assistant", response_content)

        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID is required for history retrieval")
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")
        updated_session = chat_repo.get_session(current_user.id, session_id)
        if not updated_session:
             raise HTTPException(status_code=404, detail="Session not found after message addition")
        history = [ChatMessage(role=m.role, content=m.content, created_at=m.created_at) for m in updated_session.messages]

        return ChatResponse(response=response_content, history=history, session_id=session_id)
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
    student: StudentSchema,
    preference: UserPreferenceSchema,
    advisor_service: AdvisorService = Depends(get_advisor_service),
    current_user: User = Depends(get_current_active_user),
):
    # Convert Schemas to Domain Entities
    transcript = [TranscriptEntry(**entry.model_dump()) for entry in student.transcript]
    student_domain = Student(
        id=student.id,
        name=student.name,
        transcript=transcript,
        current_skills=student.current_skills,
    )
    preference_domain = UserPreference(
        interest_tags=preference.interest_tags,
    )

    # We still need all courses for recommendation
    courses = advisor_service.course_repo.get_all()
    if not courses:
        return RecommendationResponseSchema(results=[])

    domain_response = await advisor_service.recommend(
        student_domain, courses, preference_domain, provider=DomainModelProvider.AUTO
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


@router.delete("/chat/history")
async def clear_chat_history_endpoint(
    chat_id: int = Query(..., description="The chat session ID to clear."),
    current_user: User = Depends(get_current_active_user),
    chat_history: RedisChatHistory = Depends(get_chat_history_service),
    chat_repo: ChatRepository = Depends(get_chat_repository),
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    chat_repo.delete_session(current_user.id, chat_id)
    await chat_history.clear_history(current_user.email)
    return {"status": "success"}
