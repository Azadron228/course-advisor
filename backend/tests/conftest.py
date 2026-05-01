import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_db
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
    
    app.dependency_overrides[get_db] = override_get_db
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
