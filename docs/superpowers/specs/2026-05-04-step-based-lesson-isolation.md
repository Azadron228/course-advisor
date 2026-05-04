# Design Doc: Step-Based Lesson Isolation & API Consolidation

This document outlines the shift to a plan-centric lesson model where each lesson is an isolated entity owning its content, tests, and scores, accessible through a unified step-based API.

## 1. Objectives

- **Strict Isolation**: Lessons are unique to a plan. Completing a lesson in one plan does not affect other plans.
- **Data Consolidation**: Move lesson content, tests, and scores to be associated directly with `lesson_id`.
- **API Simplification**: Consolidate all student-facing lesson interactions under the `/api/v1/learning-plan/{plan_id}/steps/{step_order}` path.
- **Removal of Redundant Layers**: Eliminate the separate `lessons` router and the practice of cloning `CourseMaterial` records for plans.

## 2. Interface Changes

### 2.1 Consolidated API Endpoints

All endpoints are prefixed with `/api/v1/learning-plan/{plan_id}/steps/{step_order}`.

| Endpoint | Method | Response | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `LessonDetail` | Returns lesson metadata, **full content**, and materials. |
| `/test` | `GET` | `PracticeTest` | Fetches or triggers generation of a practice test for this specific lesson. |
| `/test/submit` | `POST` | `Message` | Submits a score for the lesson and auto-updates the plan status. |
| `/` | `PATCH` | `LearningPlan` | Updates lesson status (existing endpoint). |

### 2.2 Schema Definitions

```python
class LessonDetail(LessonSummary):
    content: Optional[str] = None
    materials: List[LearningMaterial]
    score: Optional[int] = None
```

## 3. Data Model Changes

### 3.1 `LessonORM` Updates
- **Add Column**: `content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)`
- **Add Column**: `processed_at: Mapped[Optional[datetime]]` (optional, for tracking)

### 3.2 `UserTestScoreORM` Refactor
- **Change FK**: `material_id` -> `lesson_id` (ForeignKey to `lessons.id`).
- **Migration**: Update existing records if possible, or start fresh for the new isolated model.

### 3.3 `PracticeTestORM` Refactor
- **Change FK**: `material_id` -> `lesson_id` (ForeignKey to `lessons.id`).

## 4. Implementation Details

### 4.1 Backend
- **Alembic Migration**: 
    - Add `content` to `lessons`.
    - Update `user_test_scores` and `practice_tests` tables.
- **AdvisorService**:
    - Update `generate_learning_plan` to copy content from `CourseMaterial` to `LessonORM.content` instead of creating a new `CourseMaterial` record.
- **Repository**:
    - Implement `get_lesson_by_order(user_id, plan_id, order)`.
    - Update test-related methods to use `lesson_id`.
- **Endpoints**:
    - Remove `backend/app/api/v1/endpoints/lessons.py`.
    - Implement nested routes in `learning_plan.py`.

### 4.2 Frontend (Future Work)
- Update all calls to use the `/steps/{order}` path.
- Pass `plan_id` and `step_order` to the Lesson View and Practice Test components.

## 5. Security & Validation
- **Path Integrity**: Every request must verify that the `{plan_id}` belongs to the `current_user` and the `{step_order}` exists within that plan.
