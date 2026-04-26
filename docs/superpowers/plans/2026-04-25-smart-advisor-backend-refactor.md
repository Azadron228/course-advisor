# Smart Advisor Backend Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the backend to support persistent user profiles, AI-generated learning plans, and a unified navigation dashboard.

**Architecture:** Extend the relational schema for persistence, enhance the `AdvisorService` with Gemini-driven generation logic, and update API endpoints to expose structured data for the frontend prototype.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, LlamaIndex (Gemini), PostgreSQL/pgvector.

---

### Task 1: Database Migration

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`
- Create: `backend/alembic/versions/<timestamp>_add_profile_and_plans.py` (via `alembic revision`)

- [ ] **Step 1: Update ORM Models**
Update `UserORM` and add `UserSkillORM`, `UserTranscriptORM`, and `LearningPlanORM`.

```python
# backend/app/infrastructure/db/models.py

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disabled: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    # New fields
    career_goal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(default=False)

class UserSkillORM(Base):
    __tablename__ = "user_skills"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    mastery_level: Mapped[int] = mapped_column(default=0) # 0-100
    category: Mapped[str] = mapped_column(String, nullable=False)

class UserTranscriptORM(Base):
    __tablename__ = "user_transcripts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[float] = mapped_column(Float, nullable=False)
    mark: Mapped[float] = mapped_column(Float, nullable=False)

class LearningPlanORM(Base):
    __tablename__ = "learning_plans"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False)
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
```

- [ ] **Step 2: Generate Migration**
Run: `cd backend && alembic revision --autogenerate -m "add profile and plans"`
- [ ] **Step 3: Apply Migration**
Run: `cd backend && alembic upgrade head`
- [ ] **Step 4: Commit**
`git add backend/app/infrastructure/db/models.py backend/alembic/versions/`
`git commit -m "db: add tables for user profile and learning plans"`

---

### Task 2: Domain Entities Update

**Files:**
- Modify: `backend/app/domain/identity/entities.py`
- Modify: `backend/app/domain/recommendation/entities.py`

- [ ] **Step 1: Update User Entity**
Add `career_goal` and `onboarding_completed`.

```python
# backend/app/domain/identity/entities.py
@dataclass
class User:
    id: Optional[int]
    email: str
    full_name: Optional[str]
    disabled: bool = False
    is_admin: bool = False
    hashed_password: Optional[str] = None
    career_goal: Optional[str] = None
    onboarding_completed: bool = False
```

- [ ] **Step 2: Add Skill and Plan Entities**
```python
# backend/app/domain/recommendation/entities.py
@dataclass(frozen=True)
class UserSkill:
    skill_name: str
    mastery_level: int
    category: str

@dataclass(frozen=True)
class LearningPlan:
    id: Optional[int]
    goal: str
    steps: List[LearningPathStep]
    is_active: bool = True
```

- [ ] **Step 3: Commit**
`git add backend/app/domain/identity/entities.py backend/app/domain/recommendation/entities.py`
`git commit -m "domain: update entities for profile and learning plans"`

---

### Task 3: Repository Layer Enhancements

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/user_repository.py`
- Create: `backend/app/infrastructure/db/repositories/profile_repository.py` (for skills/transcript)
- Create: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Update UserRepository**
Update `get_by_email`, `get_by_id`, `create`, and `update` to handle new fields.
- [ ] **Step 2: Implement ProfileRepository**
Methods: `get_skills(user_id)`, `set_skills(user_id, skills)`, `get_transcript(user_id)`, `set_transcript(user_id, entries)`.
- [ ] **Step 3: Implement PlanRepository**
Methods: `get_active_plan(user_id)`, `create_plan(user_id, plan)`, `deactivate_all_plans(user_id)`.
- [ ] **Step 4: Commit**
`git add backend/app/infrastructure/db/repositories/`
`git commit -m "repo: implement profile and plan repositories"`

---

### Task 4: Advisor Service Refactor

**Files:**
- Modify: `backend/app/services/advisor_service.py`

- [ ] **Step 1: Implement `generate_learning_plan`**
Use `LLM` to create a `LearningPlan` based on `User`, `UserSkill`, and `UserTranscript`.
- [ ] **Step 2: Implement `get_skill_map`**
Generate `SkillNode`s and potentially edges based on user's current mastery.
- [ ] **Step 3: Update `recommend`**
Ensure it uses persistent data if available.
- [ ] **Step 4: Commit**
`git add backend/app/services/advisor_service.py`
`git commit -m "service: implement AI-driven plan and skill map generation"`

---

### Task 5: API Layer Update

**Files:**
- Create: `backend/app/api/v1/schemas/dashboard.py`
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`
- Modify: `backend/app/api/v1/endpoints/skills.py`
- Modify: `backend/app/api/v1/endpoints/users.py`
- Create: `backend/app/api/v1/endpoints/dashboard.py`

- [ ] **Step 1: Update Learning Plan API**
Replace mock logic with `AdvisorService.generate_learning_plan` and `PlanRepository.get_active_plan`.
- [ ] **Step 2: Update Skills API**
Replace mock logic with `AdvisorService.get_skill_map`.
- [ ] **Step 3: Implement Dashboard Endpoint**
`GET /dashboard` returning active plan progress and welcome message.
- [ ] **Step 4: Update Users API**
Add `GET /me` and `PATCH /me` for profile management.
- [ ] **Step 5: Commit**
`git add backend/app/api/v1/`
`git commit -m "api: update endpoints to support new features"`

---

### Task 6: AI Agent Contextualization

**Files:**
- Modify: `backend/app/infrastructure/ai/agent.py`
- Modify: `backend/app/api/v1/endpoints/recommendations.py`

- [ ] **Step 1: Pass Context to Agent**
Update `/chat` to include user profile and active plan in the system prompt.
- [ ] **Step 2: Verify Integration**
Ensure chat advisor can reference the user's specific learning plan.
- [ ] **Step 3: Commit**
`git add backend/app/infrastructure/ai/agent.py backend/app/api/v1/endpoints/recommendations.py`
`git commit -m "ai: contextualize advisor agent with user profile"`
