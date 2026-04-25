import punq
from functools import lru_cache
from sqlalchemy.orm import Session
from app.infrastructure.db.session import SessionLocal

from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.repositories.profile_repository import ProfileRepository
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.cache.redis_chat import RedisChatHistory
from app.domain.recommendation.scoring import ScoringService
from app.infrastructure.ai.rag import RAGScorer
from app.services.advisor_service import AdvisorService


@lru_cache(1)
def get_container() -> punq.Container:
    container = punq.Container()

    # Infrastructure
    # Note: We'll handle the Session injection via FastAPI Depends or a specific scope
    # For punq, we can register a provider that calls SessionLocal()
    container.register(Session, factory=lambda: SessionLocal())

    container.register(CourseRepository)
    container.register(UserRepository)
    container.register(ProfileRepository)
    container.register(PlanRepository)
    container.register(RedisChatHistory)
    container.register(RAGScorer)

    # Domain
    container.register(ScoringService)

    # Application Services
    container.register(AdvisorService)

    return container
