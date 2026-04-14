# Refactor Database Logic to SQLAlchemy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `backend/app/db.py` to use SQLAlchemy ORM and implement connection retry logic.

**Architecture:** Replace `psycopg2` and `sqlite3` with SQLAlchemy `engine` and `SessionLocal`. Implement `get_db` dependency for FastAPI and update CRUD functions to use SQLAlchemy ORM queries.

**Tech Stack:** SQLAlchemy, PostgreSQL (pgvector), Python.

---

### Task 1: Refactor `backend/app/db.py`

**Files:**
- Modify: `backend/app/db.py`
- Test: `tests/test_db_refactor.py`

- [ ] **Step 1: Create a test for the new database logic**

Create `tests/test_db_refactor.py` to verify the new functions. Since we might not have a running DB during build, we can use an in-memory SQLite for testing if possible, but the code is targeted at PostgreSQL. I'll create a test that can use a mock or a test DB.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db import get_all_courses, get_user_by_email, create_user
from backend.app.models import Base, CourseORM, UserORM

# Use in-memory SQLite for testing these helpers
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_and_get_user(db_session):
    email = "test@example.com"
    password = "hashed_password"
    full_name = "Test User"
    
    user = create_user(db_session, email, password, full_name)
    assert user.email == email
    
    fetched_user = get_user_by_email(db_session, email)
    assert fetched_user is not None
    assert fetched_user.email == email
    assert fetched_user.full_name == full_name

def test_get_all_courses(db_session):
    course = CourseORM(
        id="CS101",
        subject_name="Intro to CS",
        credits=3.0,
        description="Basics of CS",
        skills_taught=["Python", "Algorithms"],
        difficulty=0.2,
        workload=0.3
    )
    db_session.add(course)
    db_session.commit()
    
    courses = get_all_courses(db_session)
    assert len(courses) == 1
    assert courses[0].id == "CS101"
```

- [ ] **Step 2: Run test to verify it fails (import errors expected initially)**

Run: `pytest tests/test_db_refactor.py`

- [ ] **Step 3: Update `backend/app/db.py` with SQLAlchemy implementation**

```python
import os
import time
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .models import Base, CourseORM, UserORM

logger = logging.getLogger(__name__)

# Note: In production/docker this will be "postgresql://advisor:advisor_password@db:5432/course_advisor"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@localhost:5432/course_advisor")

# Connection retry logic
MAX_RETRIES = 5
RETRY_DELAY = 2

engine = None
# Only attempt connection if not in a test environment or if DATABASE_URL is set
if os.getenv("TESTING") != "1":
    for i in range(MAX_RETRIES):
        try:
            engine = create_engine(DATABASE_URL)
            # Test connection
            with engine.connect() as conn:
                pass
            logger.info("Successfully connected to the database")
            break
        except OperationalError as e:
            if i == MAX_RETRIES - 1:
                logger.error(f"Could not connect to database after {MAX_RETRIES} attempts")
                # Don't raise here if we want the app to at least start (e.g. for migrations)
                # but Task says to raise.
                raise e
            logger.warning(f"Database connection attempt {i+1} failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
else:
    # Minimal engine for tests if needed, but tests usually override
    engine = create_engine("sqlite:///:memory:")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Migration helpers (will use ORM versions of old functions)
def get_all_courses(db: Session):
    return db.scalars(select(CourseORM)).all()

def get_user_by_email(db: Session, email: str):
    return db.scalar(select(UserORM).where(UserORM.email == email))

def create_user(db: Session, email: str, hashed_password: str, full_name: str = None):
    db_user = UserORM(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

- [ ] **Step 4: Run tests to verify it passes**

Run: `pytest tests/test_db_refactor.py`

- [ ] **Step 5: Commit changes**

```bash
git add backend/app/db.py tests/test_db_refactor.py
git commit -m "refactor: use SQLAlchemy ORM and implement connection retry logic"
```
