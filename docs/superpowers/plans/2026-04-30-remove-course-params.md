# Remove Course Parameters and Refactor ID Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove 'difficulty', 'workload', and 'credits' from courses and refactor course ID to an autoincrementing integer.

**Architecture:** Database migration via Alembic, sequential updates to backend layers (ORM -> Domain -> Schema -> Service), and finally frontend UI cleanup.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, React, TailwindCSS.

---

### Task 1: Database Migration

**Files:**
- Create: `backend/alembic/versions/remove_course_params_and_refactor_id.py` (exact filename will have timestamp)
- Modify: `backend/app/infrastructure/db/models.py`

- [ ] **Step 1: Generate Alembic migration**

Run: `docker compose exec backend alembic revision -m "remove_course_params_and_refactor_id"`

- [ ] **Step 2: Define migration logic**

Modify the generated migration file in `backend/alembic/versions/`:

```python
def upgrade() -> None:
    # 1. Drop constraints first
    op.execute("ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_difficulty_check")
    op.execute("ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_workload_check")
    
    # 2. Drop columns
    op.drop_column('courses', 'difficulty')
    op.drop_column('courses', 'workload')
    op.drop_column('courses', 'credits')
    
    # 3. Refactor ID (Assuming no foreign keys for now as it's a prototype)
    op.execute("ALTER TABLE courses DROP CONSTRAINT courses_pkey CASCADE")
    op.drop_column('courses', 'id')
    op.add_column('courses', sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True))
    op.execute("ALTER TABLE courses ADD PRIMARY KEY (id)")

def downgrade() -> None:
    # Manual downgrade for this destructive change is not recommended, 
    # but we add columns back for completeness
    op.add_column('courses', sa.Column('id', sa.String(), primary_key=True))
    op.add_column('courses', sa.Column('credits', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('workload', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('difficulty', sa.Float(), nullable=False))
```

- [ ] **Step 3: Update SQLAlchemy Model**

Modify: `backend/app/infrastructure/db/models.py`

```python
class CourseORM(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # Changed from String
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    # credits: Mapped[float] = mapped_column(Float, nullable=False) # REMOVED
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills_taught: Mapped[dict] = mapped_column(JSON, nullable=False)
    # difficulty: Mapped[float] = mapped_column(...) # REMOVED
    # workload: Mapped[float] = mapped_column(...) # REMOVED
    materials_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
```

- [ ] **Step 4: Run migration**

Run: `docker compose exec backend alembic upgrade head`

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/ backend/app/infrastructure/db/models.py
git commit -m "db: remove course params and refactor id to int"
```

### Task 2: Update Domain Entities

**Files:**
- Modify: `backend/app/domain/catalog/entities.py`
- Modify: `backend/app/domain/recommendation/entities.py`

- [ ] **Step 1: Update Catalog Entity**

Modify: `backend/app/domain/catalog/entities.py`

```python
@dataclass(frozen=True)
class Course:
    id: int # Changed from str
    subject_name: str
    description: str
    skills_taught: List[str]
    # difficulty: float # REMOVED
    # workload: float # REMOVED
```

- [ ] **Step 2: Update Recommendation Entities**

Modify: `backend/app/domain/recommendation/entities.py`

```python
@dataclass(frozen=True)
class UserPreference:
    interest_tags: List[str]
    # target_difficulty: float # REMOVED
    # max_workload: float # REMOVED

@dataclass(frozen=True)
class ScoreBreakdown:
    skill_gap: float = 0.0
    content_sim: float = 0.0
    preference: float = 0.0
    rag_reasoning: float = 0.0
    # difficulty: float = 0.0 # REMOVED
    # load: float = 0.0 # REMOVED

@dataclass(frozen=True)
class RecommendationResult:
    course_id: int # Changed from str
    subject_name: str
    score: float
    breakdown: ScoreBreakdown
    reasoning: str
    reason_tags: List[str]
    is_external: bool = False
    url: Optional[str] = None
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/domain/catalog/entities.py backend/app/domain/recommendation/entities.py
git commit -m "domain: update entities to remove course params and fix id type"
```

### Task 3: Update API Schemas

**Files:**
- Modify: `backend/app/api/v1/schemas/course.py`
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Update Course Schemas**

Modify: `backend/app/api/v1/schemas/course.py`

```python
class CourseBase(BaseModel):
    subject_name: str
    description: str
    skills_taught: List[str]
    # difficulty: float = Field(ge=0, le=1) # REMOVED
    # workload: float = Field(ge=0, le=1) # REMOVED

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    subject_name: Optional[str] = None
    description: Optional[str] = None
    skills_taught: Optional[List[str]] = None

class Course(CourseBase):
    id: int # Changed from str
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Update Recommendation Schemas**

Modify: `backend/app/api/v1/schemas/recommendations.py`

```python
class UserPreference(BaseModel):
    interest_tags: List[str]
    # target_difficulty: float # REMOVED
    # max_workload: float # REMOVED

class ScoreBreakdown(BaseModel):
    skill_gap: float = 0.0
    content_sim: float = 0.0
    preference: float = 0.0
    rag_reasoning: float = 0.0
    # difficulty: float = 0.0 # REMOVED
    # load: float = 0.0 # REMOVED

class RecommendationResult(BaseModel):
    course_id: int # Changed from str
    # ... rest remains same
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/schemas/course.py backend/app/api/v1/schemas/recommendations.py
git commit -m "api: update schemas for removed fields"
```

### Task 4: Refactor Scoring Logic and Repositories

**Files:**
- Modify: `backend/app/domain/recommendation/scoring.py`
- Modify: `backend/app/infrastructure/db/repositories/course_repository.py`
- Modify: `backend/app/services/advisor_service.py`

- [ ] **Step 1: Remove penalties from ScoringService**

Modify: `backend/app/domain/recommendation/scoring.py`

```python
    def calculate_preference_score(self, course: Course, preference: UserPreference) -> float:
        # ... logic for tags ...
        pref_score = matches / len(tags) if tags else 0.5

        # Factor in difficulty and workload - REMOVED
        # diff_penalty = abs(course.difficulty - preference.target_difficulty)
        # work_penalty = max(0, course.workload - preference.max_workload)

        return pref_score # Just return pref_score
```

- [ ] **Step 2: Update CourseRepository mappings**

Modify: `backend/app/infrastructure/db/repositories/course_repository.py`

- [ ] **Step 3: Update AdvisorService calls**

Modify: `backend/app/services/advisor_service.py` (Search for target_difficulty and max_workload)

- [ ] **Step 4: Commit**

```bash
git add backend/app/domain/recommendation/scoring.py backend/app/infrastructure/db/repositories/course_repository.py backend/app/services/advisor_service.py
git commit -m "refactor: remove penalty logic and update repositories"
```

### Task 5: Update Seed Data and Tests

**Files:**
- Modify: `backend/seed.py`
- Modify: `backend/tests/test_admin_courses.py`

- [ ] **Step 1: Update Seed Data**

Modify: `backend/seed.py` (Remove difficulty, workload, credits from courses list)

- [ ] **Step 2: Update Tests**

Modify: `backend/tests/test_admin_courses.py` (Update payloads)

- [ ] **Step 3: Run seed and tests**

Run: `docker compose exec backend python seed.py`
Run: `docker compose exec backend pytest`

- [ ] **Step 4: Commit**

```bash
git add backend/seed.py backend/tests/test_admin_courses.py
git commit -m "test: update seed data and tests for field removal"
```

### Task 6: Frontend UI Cleanup

**Files:**
- Modify: `frontend/src/app/[locale]/admin/courses/page.tsx`
- Modify: `frontend/src/components/admin/course-form.tsx`
- Modify: `frontend/src/hooks/use-admin-courses.ts`
- Modify: `frontend/messages/en.json`, `frontend/messages/ru.json`

- [ ] **Step 1: Update use-admin-courses Hook**

Modify: `frontend/src/hooks/use-admin-courses.ts` (Update Course interface)

- [ ] **Step 2: Update Course Form Component**

Modify: `frontend/src/components/admin/course-form.tsx` (Remove difficulty, workload inputs)

- [ ] **Step 3: Update Admin Course List**

Modify: `frontend/src/app/[locale]/admin/courses/page.tsx` (Remove difficulty/workload columns/display)

- [ ] **Step 4: Cleanup Translations**

Modify: `frontend/messages/en.json`, `frontend/messages/ru.json` (Optionally remove unused keys)

- [ ] **Step 5: Verify Frontend**

Run: `npm run build` in `frontend/` (if possible) or visually verify.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "ui: remove course params from admin and list"
```
