# Design Doc: Merge Lessons API into Learning Plan API

## Overview
This design aims to consolidate all lesson-related endpoints into the Learning Plan API, specifically utilizing the path pattern `/api/v1/learning-plan/{plan_id}/lessons/{step_order}`. This provides a more hierarchical and context-aware API structure.

## Architectural Changes

### 1. Service Layer Delegation
- `LearningPlanService` will be updated to depend on `LessonService`.
- `LearningPlanService` will act as an orchestrator, translating `step_order` within a specific `plan_id` to a `lesson_id`, and then delegating the actual work to `LessonService`.

### 2. API Endpoint Migration
- Standalone `/api/v1/lessons/{lesson_id}` endpoints will be removed.
- Equivalent functionality will be exposed under `/api/v1/learning-plan/{plan_id}/lessons/{step_order}`.

## New/Updated Endpoints

### Learning Plan API (v1)

| Method | Path | Description | Service Method |
|--------|------|-------------|----------------|
| GET | `/{plan_id}/lessons/{step_order}` | Get lesson detail (triggers content generation) | `LearningPlanService.get_step_detail` |
| PATCH | `/{plan_id}/lessons/{step_order}` | Update lesson status | `LearningPlanService.update_plan_step` |
| GET | `/{plan_id}/lessons/{step_order}/test` | Get practice test for the step | `LearningPlanService.get_step_test` |
| POST | `/{plan_id}/lessons/{step_order}/test/submit` | Submit practice test for the step | `LearningPlanService.submit_step_test` |

## Service Layer Updates

### `LearningPlanService`
- Constructor updated to accept `LessonService`.
- `get_step_detail(user, plan_id, step_order)`: Becomes `async`. Resolves `lesson_id` from `step_order`, calls `lesson_service.get_lesson_detail(user, lesson_id)`.
- `update_plan_step(...)`: Updated to use `lesson_service.update_lesson_status` for consistent status management.
- `get_step_test(user, plan_id, step_order)`: **New**. Resolves `lesson_id`, calls `lesson_service.get_practice_test(user, lesson_id)`.
- `submit_step_test(user, plan_id, step_order, submission)`: **New**. Resolves `lesson_id`, calls `lesson_service.submit_test(user, lesson_id, submission)`.

### `LessonService`
- Remains largely unchanged, continuing to provide core lesson logic (content generation, test generation, scoring).

## Infrastructure Updates

### `app/api/deps.py`
- `get_learning_plan_service` will now also depend on `get_lesson_service` to provide the required dependency for `LearningPlanService`.

### `app/api/router.py`
- Remove the registration of the standalone `lessons` router.

## Testing Strategy
- Update existing tests in `backend/tests/test_practice_tests.py` and `backend/tests/test_learning_plan_redesign.py` to use the new hierarchical paths.
- Verify that content generation is still triggered correctly on the new detail endpoint.
- Ensure that unauthorized access (wrong user or wrong plan) is still correctly handled at the service level.
