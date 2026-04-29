from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from app.infrastructure.db.models import ChatSessionORM, ChatMessageORM
from app.domain.recommendation.entities import ChatSession, ChatMessage


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def _session_to_domain(self, o: ChatSessionORM, messages: List[ChatMessage] = None) -> ChatSession:
        return ChatSession(
            id=o.id,
            user_id=o.user_id,
            title=o.title,
            created_at=o.created_at,
            updated_at=o.updated_at,
            messages=messages or []
        )

    def _message_to_domain(self, o: ChatMessageORM) -> ChatMessage:
        return ChatMessage(
            role=o.role,
            content=o.content,
            created_at=o.created_at
        )

    def list_sessions(self, user_id: int) -> List[ChatSession]:
        objs = self.db.scalars(
            select(ChatSessionORM)
            .where(ChatSessionORM.user_id == user_id)
            .order_by(ChatSessionORM.updated_at.desc())
        ).all()
        return [self._session_to_domain(o) for o in objs]

    def get_session(self, user_id: int, session_id: int) -> Optional[ChatSession]:
        o = self.db.scalar(
            select(ChatSessionORM)
            .where(ChatSessionORM.id == session_id)
            .where(ChatSessionORM.user_id == user_id)
        )
        if not o:
            return None
        
        message_objs = self.db.scalars(
            select(ChatMessageORM)
            .where(ChatMessageORM.session_id == session_id)
            .order_by(ChatMessageORM.created_at.asc())
        ).all()
        
        messages = [self._message_to_domain(m) for m in message_objs]
        return self._session_to_domain(o, messages)

    def create_session(self, user_id: int, title: str) -> ChatSession:
        now = datetime.utcnow().isoformat()
        db_session = ChatSessionORM(
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return self._session_to_domain(db_session)

    def add_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        now = datetime.utcnow().isoformat()
        db_message = ChatMessageORM(
            session_id=session_id,
            role=role,
            content=content,
            created_at=now
        )
        self.db.add(db_message)
        
        # Update session updated_at
        self.db.execute(
            update(ChatSessionORM)
            .where(ChatSessionORM.id == session_id)
            .values(updated_at=now)
        )
        
        self.db.commit()
        self.db.refresh(db_message)
        return self._message_to_domain(db_message)

    def delete_session(self, user_id: int, session_id: int):
        # Delete messages first
        self.db.execute(
            delete(ChatMessageORM).where(ChatMessageORM.session_id == session_id)
        )
        # Delete session
        self.db.execute(
            delete(ChatSessionORM)
            .where(ChatSessionORM.id == session_id)
            .where(ChatSessionORM.user_id == user_id)
        )
        self.db.commit()

    def clear_user_sessions(self, user_id: int):
        session_ids = self.db.scalars(
            select(ChatSessionORM.id).where(ChatSessionORM.user_id == user_id)
        ).all()
        
        if session_ids:
            self.db.execute(
                delete(ChatMessageORM).where(ChatMessageORM.session_id.in_(session_ids))
            )
            self.db.execute(
                delete(ChatSessionORM).where(ChatSessionORM.user_id == user_id)
            )
            self.db.commit()
