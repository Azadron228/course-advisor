# Design Doc: Learning Plan API Redesign

This document outlines the redesign of the Learning Plan API to optimize data delivery, improve performance, and track user engagement.

## 1. Objectives

- **Reduce Payload Size**: Optimize `List Learning Plans` and `Get Plan By Id` to return only necessary data.
- **Improved Data Hierarchy**: Separate high-level plan metadata from detailed lesson content.
- **Engagement Tracking**: Track and sort plans by the "last interacted" timestamp.
- **On-Demand Loading**: Fetch lesson materials only when specifically requested.

## 2. Interface Design

### 2.1 API Endpoints

| Endpoint | Method | Response Model | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/learning-plan/` | `GET` | `List[LearningPlanSummary]` | Returns all plans for the current user, sorted by `last_interacted_at` DESC. Includes `step_count`. |
| `/api/v1/learning-plan/{plan_id}` | `GET` | `LearningPlanDetail` | Returns plan metadata and a list of `LessonSummary` (no materials). |
| `/api/v1/learning-plan/{plan_id}/lessons/{lesson_id}` | `GET` | `LessonDetail` | Returns full lesson details including the list of assigned `materials`. |

### 2.2 Schema Definitions

```python
class LessonSummary(BaseModel):
    id: int
    order: int
    title: str
    description: str
    status: str
    score: Optional[int] = None
    is_external: bool

class LearningPlanSummary(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    step_count: int

class LearningPlanDetail(BaseModel):
    id: int
    goal: str
    is_active: bool
    last_interacted_at: datetime
    steps: List[LessonSummary]

class LessonDetail(LessonSummary):
    materials: List[LearningMaterial]
```

## 3. Data Model Changes

### 3.1 Database Schema (`learning_plans` table)

- **Add Column**: `last_interacted_at: DateTime`
    - Default: `now()` (UTC)
    - Nullable: No

### 3.2 Update Triggers

The `last_interacted_at` timestamp MUST be updated (set to `now()`) during the following operations:

1. **Plan Generation**: Initial creation of the plan.
2. **Status Update**: Any call to `PATCH /api/v1/learning-plan/{plan_id}/steps/{step_order}` or `PATCH /api/v1/lessons/{lesson_id}/status`.
3. **Test Submission**: When a score is saved via `POST /api/v1/lessons/{material_id}/test/submit`.

## 4. Implementation Details

### 4.1 Backend
- **Alembic Migration**: Add the `last_interacted_at` column.
- **Repository**:
    - Update `PlanRepository.get_all_plans` to use a JOIN or subquery for `step_count` and apply sorting.
    - Add `PlanRepository.update_last_interacted(plan_id)`.
    - Implement `PlanRepository.get_lesson_with_materials(lesson_id)`.
- **Endpoints**:
    - Refactor `learning_plan.py` to use new schemas.
    - Implement the new nested lesson detail endpoint.

### 4.2 Frontend (Future Work)
- Update API services to use the new summary/detail split.
- Update the learning page to fetch materials using the new dedicated endpoint when a lesson is selected.

## 5. Security & Validation

- **Ownership**: All endpoints must verify that the requested `plan_id` or `lesson_id` belongs to the `current_user`.
- **Data Integrity**: Ensure that `step_count` accurately reflects the number of lessons in the database.
- **Sorting**: Verify that plans are correctly sorted by interaction time.
