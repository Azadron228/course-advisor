# Separate Lessons Table Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor learning plan storage from a JSON blob to a structured `lessons` table to improve data integrity and queryability.

**Architecture:** Introduce `LessonORM` with a many-to-one relationship to `LearningPlanORM`. Update the domain layer and repositories to handle this relational structure, replacing the legacy JSON `steps` field.

**Tech Stack:** Python (FastAPI), SQLAlchemy (ORM), Alembic (Migrations), Pydantic (Domain).

---

### Task 1: Database Migration

**Files:**
- Create: `backend/alembic/versions/2026_05_04_add_lessons_table.py`

- [ ] **Step 1: Generate the migration script**

Run: `alembic revision -m "add lessons table"`

- [ ] **Step 2: Implement the migration**

```python
"""add lessons table

Revision ID: <revision_id>
Revises: <previous_revision_id>
Create Date: 2026-05-04 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('learning_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('course_materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='upcoming'),
        sa.Column('is_external', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('external_url', sa.String(), nullable=True),
        sa.Column('additional_resources', sa.JSON(), nullable=False, server_default='[]'),
    )
    op.create_index(op.f('ix_lessons_order'), 'lessons', ['order'], unique=False)

    # Drop steps from learning_plans
    op.drop_column('learning_plans', 'steps')

def downgrade():
    op.add_column('learning_plans', sa.Column('steps', sa.JSON(), nullable=True))
    op.drop_table('lessons')
```

- [ ] **Step 3: Run the migration**

Run: `alembic upgrade head`
Expected: SUCCESS

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/versions/*.py
git commit -m "db: add lessons table and remove steps from learning_plans"
```

### Task 2: ORM Models Update

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`

- [ ] **Step 1: Update LearningPlanORM and add LessonORM**

```python
# In backend/app/infrastructure/db/models.py

class LearningPlanORM(Base):
    __tablename__ = "learning_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False)
    # steps column removed
    is_active: Mapped[bool] = mapped_column(default=True)
    skill_level: Mapped[str] = mapped_column(String, nullable=False, default="Beginner")
    learning_style: Mapped[str] = mapped_column(String, nullable=False, default="Practical")
    study_time: Mapped[int] = mapped_column(default=10)
    interests: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # New relationship
    lessons: Mapped[List["LessonORM"]] = relationship(
        "LessonORM", back_populates="plan", cascade="all, delete-orphan", order_by="LessonORM.order"
    )

class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False)
    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("course_materials.id", ondelete="SET NULL"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="upcoming")
    is_external: Mapped[bool] = mapped_column(default=False)
    external_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    additional_resources: Mapped[List[dict]] = mapped_column(JSON, nullable=False, default=list)

    plan: Mapped["LearningPlanORM"] = relationship("LearningPlanORM", back_populates="lessons")
    material: Mapped[Optional["CourseMaterialORM"]] = relationship("CourseMaterialORM")
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/infrastructure/db/models.py
git commit -m "feat: update ORM models for relational learning plans"
```

### Task 3: Domain Models Update

**Files:**
- Modify: `backend/app/domain/recommendation/entities.py`

- [ ] **Step 1: Rename LearningPathStep to Lesson and add id**

```python
# In backend/app/domain/recommendation/entities.py

class Lesson(BaseModel): # Renamed from LearningPathStep
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None # Keeping as str for compatibility, will map to material_id
    is_external: bool = False
    external_url: Optional[str] = None
    status: str = "upcoming"
    materials: List[LearningMaterial] = Field(default_factory=list) # maps to additional_resources
    score: Optional[int] = None

# Update LearningPlan to use Lesson
class LearningPlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    goal: str
    steps: List[Lesson] = Field(default_factory=list) # Keeping 'steps' name for now, or rename to lessons
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = Field(default_factory=list)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/domain/recommendation/entities.py
git commit -m "feat: update domain entities for relational lessons"
```

### Task 4: Repository Layer Update

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Update PlanRepository to handle lessons relationship**

```python
# In backend/app/infrastructure/db/repositories/plan_repository.py

from sqlalchemy.orm import selectinload
from app.infrastructure.db.models import LearningPlanORM, LessonORM, UserTestScoreORM

class PlanRepository:
    # ...
    def _to_domain(self, o: LearningPlanORM) -> LearningPlan:
        # Collect material IDs for scores
        material_ids = [l.material_id for l in o.lessons if l.material_id]
        
        scores_map = {}
        if material_ids:
            scores = self.db.execute(
                select(UserTestScoreORM)
                .where(UserTestScoreORM.user_id == o.user_id)
                .where(UserTestScoreORM.material_id.in_(material_ids))
            ).scalars().all()
            scores_map = {s.material_id: s.score for s in scores}

        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[
                Lesson(
                    id=l.id,
                    order=l.order,
                    title=l.title,
                    description=l.description,
                    resource_id=str(l.material_id) if l.material_id else None,
                    is_external=l.is_external,
                    external_url=l.external_url,
                    status=l.status,
                    materials=[LearningMaterial(**m) for m in l.additional_resources],
                    score=scores_map.get(l.material_id) if l.material_id else None
                ) 
                for l in o.lessons
            ],
            is_active=o.is_active,
            skill_level=o.skill_level,
            learning_style=o.learning_style,
            study_time=o.study_time,
            interests=o.interests,
        )

    def get_active_plan(self, user_id: int) -> Optional[LearningPlan]:
        o = self.db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.user_id == user_id)
            .where(LearningPlanORM.is_active == True)
        )
        if not o: return None
        return self._to_domain(o)

    def create_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        db_plan = LearningPlanORM(
            user_id=user_id,
            goal=plan.goal,
            is_active=plan.is_active,
            skill_level=plan.skill_level,
            learning_style=plan.learning_style,
            study_time=plan.study_time,
            interests=plan.interests
        )
        self.db.add(db_plan)
        self.db.flush() # Get ID

        for s in plan.steps:
            lesson = LessonORM(
                plan_id=db_plan.id,
                order=s.order,
                title=s.title,
                description=s.description,
                material_id=int(s.resource_id) if s.resource_id and not s.is_external else None,
                is_external=s.is_external,
                external_url=s.external_url,
                status=s.status,
                additional_resources=[m.model_dump() for m in s.materials]
            )
            self.db.add(lesson)
        
        self.db.commit()
        self.db.refresh(db_plan)
        return self._to_domain(db_plan)
    
    # Update update_plan to handle lesson updates
    def update_plan(self, user_id: int, plan: LearningPlan) -> LearningPlan:
        # ... fetch o ...
        # Clear existing lessons (or perform diff update)
        # For simplicity in this spec: clear and recreate
        for lesson in o.lessons:
            self.db.delete(lesson)
        self.db.flush()

        for s in plan.steps:
             # Add new LessonORM records ...
        
        self.db.commit()
        return self._to_domain(o)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "feat: implement relational logic in PlanRepository"
```

### Task 5: Service Layer Update

**Files:**
- Modify: `backend/app/services/advisor_service.py`

- [ ] **Step 1: Update generate_learning_plan to use Lesson entities**

Update `generate_learning_plan` to correctly instantiate the new `Lesson` domain entity and handle the material cloning correctly. Ensure it updates the `material_id` (via `resource_id` mapping) on the specific lesson.

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/advisor_service.py
git commit -m "feat: update AdvisorService for relational plans"
```

### Task 6: API Layer & Testing

**Files:**
- Modify: `backend/app/api/v1/routes.py` (or where the routes are)
- Create: `backend/tests/test_lessons.py`

- [ ] **Step 1: Add/Update API endpoints for lessons**
- [ ] **Step 2: Write integration tests for plan generation and lesson status updates**
- [ ] **Step 3: Commit**

---
