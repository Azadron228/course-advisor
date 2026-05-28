import logging
import re
from typing import List, Optional, AsyncGenerator
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.recommendations import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatSession as ChatSessionSchema,
    ChatSessionDetail as ChatSessionDetailSchema,
)
from app.domain.recommendation.entities import (
    ModelProvider as DomainModelProvider,
)
from app.infrastructure.cache.redis_chat import RedisChatHistory
from app.infrastructure.db.repositories.chat_repository import ChatRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.ai.agent import get_advisor_agent
from app.infrastructure.ai.model_factory import get_model
from llama_index.core.base.llms.types import ChatMessage as LLMChatMessage, MessageRole
from llama_index.core.agent.workflow.workflow_events import AgentStream, AgentOutput
from app.domain.identity.entities import User

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        chat_history: RedisChatHistory,
        profile_repo: ProfileRepository,
        plan_repo: PlanRepository,
        db: Session,
    ):
        self.chat_repo = chat_repo
        self.chat_history = chat_history
        self.profile_repo = profile_repo
        self.plan_repo = plan_repo
        self.db = db

    def list_sessions(self, user_id: int) -> List[ChatSessionSchema]:
        sessions = self.chat_repo.list_sessions(user_id)
        return [ChatSessionSchema.model_validate(s) for s in sessions]

    def get_session(self, user_id: int, session_id: int) -> Optional[ChatSessionDetailSchema]:
        session = self.chat_repo.get_session(user_id, session_id)
        if not session:
            return None
        return ChatSessionDetailSchema.model_validate(session)

    async def delete_session(self, user: User, session_id: int):
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")
        self.chat_repo.delete_session(user.id, session_id)
        await self.chat_history.clear_history(user.email)

    async def handle_chat(self, user: User, request: ChatRequest) -> ChatResponse:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Retrieve user profile context
        skills = self.profile_repo.get_skills(user.id)
        transcript = self.profile_repo.get_transcript(user.id)
        active_plan = self.plan_repo.get_active_plan(user.id)

        # Format context strings
        transcript_summary = (
            ", ".join(
                [f"{e.subject_name} (Credits: {e.credits}, Mark: {e.mark})" for e in transcript]
            )
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
            title = request.message[:50] + ("..." if len(request.message) > 50 else "")
            session = self.chat_repo.create_session(user.id, title)
            session_id = session.id
            await self.chat_history.clear_history(user.email)

        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID is required")

        session = self.chat_repo.get_session(user.id, session_id)
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
            user=user,
            learning_plan=active_plan,
        )

        logger.info(
            f"Chat request from user {user.email} for session {session_id}: {request.message[:50]}..."
        )

        handler = agent.run(user_msg=request.message, chat_history=chat_messages)
        result = await handler

        response_content = ""
        if isinstance(result, AgentOutput):
            response_content = str(result.response)
            if re.search(r"(?:^|\n)Final Answer:", response_content):
                response_content = re.split(r"(?:^|\n)Final Answer:", response_content)[-1].strip()
        else:
            response_content = str(result)

        # Save to DB
        self.chat_repo.add_message(session_id, "user", request.message)
        self.chat_repo.add_message(session_id, "assistant", response_content)

        # Also save to Redis
        await self.chat_history.add_message(user.email, "user", request.message)
        await self.chat_history.add_message(user.email, "assistant", response_content)

        updated_session = self.chat_repo.get_session(user.id, session_id)
        if not updated_session:
            raise HTTPException(status_code=404, detail="Session not found after message addition")

        history = [
            ChatMessage(role=m.role, content=m.content, created_at=m.created_at)
            for m in updated_session.messages
        ]

        return ChatResponse(response=response_content, history=history, session_id=session_id)

    async def stream_chat(self, user: User, request: ChatRequest) -> AsyncGenerator[str, None]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Retrieve user profile context
        skills = self.profile_repo.get_skills(user.id)
        transcript = self.profile_repo.get_transcript(user.id)
        active_plan = self.plan_repo.get_active_plan(user.id)

        # Format context strings
        transcript_summary = (
            ", ".join(
                [f"{e.subject_name} (Credits: {e.credits}, Mark: {e.mark})" for e in transcript]
            )
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
            title = request.message[:50] + ("..." if len(request.message) > 50 else "")
            session = self.chat_repo.create_session(user.id, title)
            session_id = session.id
            await self.chat_history.clear_history(user.email)

        if session_id is None:
            raise HTTPException(status_code=400, detail="Session ID is required")

        session = self.chat_repo.get_session(user.id, session_id)
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
            user=user,
            learning_plan=active_plan,
        )

        handler = agent.run(user_msg=request.message, chat_history=chat_messages)

        full_response = ""
        final_answer_started = False
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                if getattr(event, "thinking_delta", None):
                    continue

                delta = event.delta
                full_response += delta

                if not final_answer_started:
                    if re.search(r"(?:^|\n)Final Answer:", full_response):
                        final_answer_started = True
                        parts = re.split(r"(?:^|\n)Final Answer:", full_response)
                        part = parts[-1].lstrip()
                        if part:
                            yield part
                else:
                    yield delta

        if not final_answer_started and full_response:
            clean_response = full_response
            if re.search(r"(?:^|\n)Final Answer:", clean_response):
                clean_response = re.split(r"(?:^|\n)Final Answer:", clean_response)[-1].strip()
            yield clean_response

        # Final cleanup and save
        clean_response = full_response
        if re.search(r"(?:^|\n)Final Answer:", clean_response):
            clean_response = re.split(r"(?:^|\n)Final Answer:", clean_response)[-1].strip()

        self.chat_repo.add_message(session_id, "user", request.message)
        self.chat_repo.add_message(session_id, "assistant", clean_response)
        await self.chat_history.add_message(user.email, "user", request.message)
        await self.chat_history.add_message(user.email, "assistant", clean_response)

    async def get_history(self, user: User) -> List[ChatMessage]:
        history_dicts = await self.chat_history.get_history(user.email)
        return [ChatMessage(**m) for m in history_dicts]
