# Design Doc: Fetch Lessons by Step Order

This document describes the change from fetching lesson details by their database ID to fetching them by their sequential order within a learning plan.

## 1. Objectives

- **Consistency**: Align the `GET` endpoint with the existing `PATCH` endpoint which uses `step_order`.
- **Frontend Simplicity**: Allow the frontend to fetch lesson details using the same index it uses for display and status updates.
- **API Cleanup**: Remove the internal `lesson_id` from the public-facing learning plan API.

## 2. Interface Changes

### 2.1 API Endpoints

| Old Endpoint | New Endpoint | Method | Response |
| :--- | :--- | :--- | :--- |
| `/api/v1/learning-plan/{plan_id}/lessons/{lesson_id}` | `/api/v1/learning-plan/{plan_id}/steps/{step_order}` | `GET` | `LessonDetail` |

## 3. Implementation Details

### 3.1 Repository Enhancements (`PlanRepository`)

- **Add Method**: `get_lesson_by_order(user_id: int, plan_id: int, step_order: int) -> Optional[LessonDetail]`
    - Logic: Join `LessonORM` with `LearningPlanORM`, filter by `user_id`, `plan_id`, and `order`.
- **Remove/Deprecate**: `get_lesson_with_materials` (if it only supported `lesson_id`).

### 3.2 Endpoint Refactoring (`learning_plan.py`)

- Update the route path from `/lessons/{lesson_id}` to `/steps/{step_order}`.
- Update the function signature and logic to use `plan_repo.get_lesson_by_order`.

## 4. Verification Plan

- **Integration Tests**: Update `tests/test_learning_plan_redesign.py` to use the new path and verify that lesson details (including materials) are correctly returned for a given order.
- **Manual Verification**: Verify that requesting an out-of-bounds `step_order` returns a 404.
