import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db, get_container
from app.infrastructure.db.models import Base, UserORM
from app.core.security import get_password_hash, create_access_token

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_container():
        import punq
        from sqlalchemy.orm import Session
        from app.infrastructure.db.repositories.user_repository import UserRepository
        from app.infrastructure.db.repositories.profile_repository import ProfileRepository
        from app.infrastructure.db.repositories.plan_repository import PlanRepository
        from app.infrastructure.db.repositories.chat_repository import ChatRepository
        from app.infrastructure.cache.redis_chat import RedisChatHistory
        from app.services.advisor_service import AdvisorService
        from app.services.learning_plan_service import LearningPlanService
        from app.services.lesson_service import LessonService
        from app.services.chat_service import ChatService

        container = punq.Container()
        container.register(Session, instance=db)
        container.register(UserRepository)
        container.register(ProfileRepository)
        container.register(PlanRepository)
        container.register(ChatRepository)
        container.register(RedisChatHistory)
        container.register(AdvisorService)
        container.register(LearningPlanService)
        container.register(LessonService)
        container.register(ChatService)
        return container

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_container] = override_get_container
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    user = UserORM(
        email="admin@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Admin User",
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token_headers(admin_user):
    access_token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def normal_user(db):
    user = UserORM(
        email="user@example.com",
        hashed_password=get_password_hash("password"),
        full_name="Normal User",
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user_token_headers(normal_user):
    access_token = create_access_token(data={"sub": normal_user.email})
    return {"Authorization": f"Bearer {access_token}"}
