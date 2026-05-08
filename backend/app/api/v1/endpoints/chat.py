import logging
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.schemas.recommendations import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatSession as ChatSessionSchema,
    ChatSessionDetail as ChatSessionDetailSchema,
)
from app.api.v1.schemas.auth import UserPublic as User
from app.services.chat_service import ChatService
from app.api.deps import (
    get_current_active_user,
    get_chat_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions", response_model=List[ChatSessionSchema])
async def list_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    return service.list_sessions(current_user.id)


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailSchema)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    session = service.get_session(current_user.id, session_id)
    return session


@router.delete("/{chat_id}")
async def delete_chat_session(
    chat_id: int,
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    await service.delete_session(current_user, chat_id)
    return {"status": "success"}


@router.post("", response_model=ChatResponse)
async def chat_with_advisor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    if request.stream:
        return StreamingResponse(service.stream_chat(current_user, request), media_type="text/event-stream")

    return await service.handle_chat(current_user, request)


@router.get("/history", response_model=List[ChatMessage])
async def get_chat_history_endpoint(
    current_user: User = Depends(get_current_active_user),
    service: ChatService = Depends(get_chat_service),
):
    return await service.get_history(current_user)
