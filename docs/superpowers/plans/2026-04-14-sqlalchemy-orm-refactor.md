# SQLAlchemy ORM and Email-based Auth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the backend to use SQLAlchemy ORM, replace SQLite with PostgreSQL for user storage, and switch to email-based authentication.

**Architecture:**
- Use SQLAlchemy `DeclarativeBase` for ORM models.
- Implement a `get_db` dependency for FastAPI.
- Use Alembic for database migrations.
- Update Pydantic schemas to align with email-based auth.
- Remove all SQLite dependencies.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL (pgvector), Alembic, Pydantic, Argon2.

---

### Task 1: Update Models with SQLAlchemy ORM

**Files:**
- Modify: `backend/app/models.py`

- [ ] **Step 1: Define SQLAlchemy Base and Models**

Add SQLAlchemy ORM models for `User` and `Course`. Update Pydantic schemas to use `email` instead of `username`.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, JSON, CheckConstraint, Text
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum

class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disabled: Mapped[bool] = mapped_column(default=False)

class CourseORM(Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills_taught: Mapped[dict] = mapped_column(JSON, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, CheckConstraint('difficulty >= 0 AND difficulty <= 1'))
    workload: Mapped[float] = mapped_column(Float, CheckConstraint('workload >= 0 AND workload <= 1'))
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))

# Update Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(User):
    id: int

class UserInDB(User):
    hashed_password: str

# (Keep other models like Course, TranscriptEntry, etc. but update Course if needed)
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/models.py
git commit -m "feat: add SQLAlchemy ORM models and update Pydantic schemas for email auth"
```

---

### Task 2: Refactor Database Logic to SQLAlchemy

**Files:**
- Modify: `backend/app/db.py`

- [ ] **Step 1: Replace psycopg2/sqlite3 with SQLAlchemy engine and session**

Implement `get_db` dependency and connection retry logic.

```python
import os
import time
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .models import Base, CourseORM, UserORM

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@db:5432/course_advisor")

# Connection retry logic
MAX_RETRIES = 5
RETRY_DELAY = 2

engine = None
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
            raise e
        logger.warning(f"Database connection attempt {i+1} failed. Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)

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

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/db.py
git commit -m "refactor: use SQLAlchemy ORM and implement connection retry logic"
```

---

### Task 3: Create Database Migration for Users Table

**Files:**
- Create: `backend/alembic/versions/<id>_add_users_table.py`
- Modify: `backend/alembic/env.py`

- [ ] **Step 1: Point Alembic to models metadata**

In `backend/alembic/env.py`:
```python
from app.models import Base
target_metadata = Base.metadata
```

- [ ] **Step 2: Create migration for users table**

Run: `docker-compose exec backend alembic revision -m "add users table"`
Or create manually if docker is not running:
```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('disabled', sa.Boolean(), default=False)
    )
```

- [ ] **Step 3: Apply migrations**

Run: `docker-compose exec backend alembic upgrade head`

- [ ] **Step 4: Commit migration**

```bash
git add backend/alembic/env.py backend/alembic/versions/*
git commit -m "feat: add alembic migration for users table"
```

---

### Task 4: Update Authentication Logic

**Files:**
- Modify: `backend/app/auth.py`

- [ ] **Step 1: Update auth functions to use email and SQLAlchemy**

```python
from .db import get_user_by_email
from sqlalchemy.orm import Session

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # ... decode JWT ...
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = get_user_by_email(db, email)
    # ...
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/auth.py
git commit -m "refactor: update auth logic to use email and SQLAlchemy"
```

---

### Task 5: Refactor Main App Endpoints

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update register and login endpoints**

```python
@app.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    create_user(db, user.email, hashed_password, user.full_name)
    return User(email=user.email, full_name=user.full_name)

@app.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password) # form_data.username will contain email
    # ...
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/main.py
git commit -m "refactor: update FastAPI endpoints to use SQLAlchemy and email auth"
```

---

### Task 6: Refactor Scoring Components to SQLAlchemy

**Files:**
- Modify: `backend/app/scoring/content.py`
- Modify: `backend/app/scoring/orchestrator.py`
- Modify: `backend/app/scoring/rag.py`
- Modify: `backend/app/scoring/preference.py`
- Modify: `backend/app/scoring/skill_gap.py`

- [ ] **Step 1: Update ContentScorer to use SQLAlchemy session**

```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import CourseORM

class ContentScorer:
    def score(self, db: Session, student: Student, course_id: str) -> float:
        # ...
        course = db.scalar(select(CourseORM).where(CourseORM.id == course_id))
        if course and course.embedding:
            # Use pgvector similarity logic with SQLAlchemy if possible, 
            # or keep raw query via db.execute()
            result = db.execute(
                select(1 - CourseORM.embedding.cosine_distance(vector))
                .where(CourseORM.id == course_id)
            ).scalar()
            return float(result) if result else 0.0
        return 0.0
```

- [ ] **Step 2: Update HybridScorer to accept and pass Session**

Update `recommend` method to take `db: Session`.

- [ ] **Step 3: Commit changes**

```bash
git add backend/app/scoring/*.py
git commit -m "refactor: update scoring components to use SQLAlchemy sessions"
```

---

### Task 7: Cleanup and Verification

- [ ] **Step 1: Delete `users.db` and SQLite imports**

- [ ] **Step 2: Run tests**

Run: `pytest tests/` (Verify all tests pass with the new architecture)

- [ ] **Step 3: Commit cleanup**

```bash
git rm users.db
git commit -m "cleanup: remove SQLite database and legacy imports"
```
