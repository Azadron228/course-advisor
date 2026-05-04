# Design Spec: Separate Lessons Table for Learning Plans

## Goal
Refactor the learning plan architecture to move steps from a JSON blob within the `learning_plans` table into a separate, structured `lessons` table. This ensures data integrity, enables easier querying of progress across plans, and establishes a clean many-to-one relationship between lessons and plans.

## Architecture

### Database Schema

#### `LearningPlanORM` (Updated)
- `id`: Integer (PK, Autoincrement)
- `user_id`: Integer (FK to `users.id`)
- `goal`: String
- `is_active`: Boolean
- `skill_level`: String
- `learning_style`: String
- `study_time`: Integer
- `interests`: JSON
- **Relationships**:
    - `lessons`: `relationship("LessonORM", back_populates="plan", cascade="all, delete-orphan")`

#### `LessonORM` (New Table)
- `id`: Integer (PK, Autoincrement)
- `plan_id`: Integer (FK to `learning_plans.id`, ondelete="CASCADE")
- `material_id`: Integer (FK to `course_materials.id`, ondelete="SET NULL", nullable=True)
- `order`: Integer (Index for sequence)
- `title`: String
- `description`: Text
- `status`: String (Enum: `upcoming`, `current`, `completed`)
- `is_external`: Boolean
- `external_url`: String (Nullable)
- `additional_resources`: JSON (List of `LearningMaterial` objects)
- **Relationships**:
    - `plan`: `relationship("LearningPlanORM", back_populates="lessons")`
    - `material`: `relationship("CourseMaterialORM")`

### Domain Layer

- Update `LearningPlan` domain entity to reflect that `steps` are now `Lesson` entities.
- Update `LearningPathStep` (rename to `Lesson` in domain if appropriate, but keeping name for compatibility for now) to include a proper `id`.

### Repository Layer

#### `PlanRepository`
- `_to_domain`: Update to fetch lessons via the relationship instead of parsing JSON.
- `create_plan`: Bulk insert `LessonORM` records after creating the plan.
- `update_plan`: Update lessons (handle add/remove/update logic).
- `get_active_plan`: Include lessons in the query using `selectinload`.

#### `LessonRepository` (New or part of PlanRepository)
- `update_lesson_status(lesson_id, status)`: Direct update of a lesson's progress.

### Service Layer

#### `AdvisorService`
- Update `generate_learning_plan` to create `LessonORM` instances.
- When cloning materials, update the `material_id` on the specific `LessonORM` record.

## API Changes

### New Endpoints
- `PATCH /api/v1/lessons/{lesson_id}`:
    - Body: `{"status": "completed" | "current" | "upcoming"}`
    - Logic: Update the lesson status and automatically unlock the next lesson in the same plan.

### Modified Endpoints
- `GET /api/v1/learning_plan/` & `GET /api/v1/learning_plan/{id}`:
    - Response structure remains mostly compatible (returning a list of lessons/steps), but uses the new relational data.

## Migration Strategy
- Since the user approved deleting existing data:
    1. Drop existing `learning_plans` and `course_materials` (or at least those tied to plans).
    2. Apply new schema.
    3. Re-generate plans as needed.

## Testing Strategy
- **Unit Tests**: Verify `PlanRepository` correctly saves and retrieves lessons.
- **Integration Tests**: Verify `AdvisorService` creates the full relational structure during generation.
- **E2E Tests**: Verify that submitting a test for a material correctly updates the status of the associated lesson in the new table.
