# Design Doc: Refactoring Endpoints to Services

## Goal
Refactor the backend architecture to move business logic from API endpoints to dedicated service layers, following the project's architecture principles of layered design and separation of concerns.

## Proposed Changes

### 1. New Services
- **`LearningPlanService`**: Responsible for learning plan lifecycle.
  - `generate_plan(user, request, arq_pool)`
  - `list_user_plans(user_id)`
  - `get_plan_detail(user_id, plan_id)`
  - `delete_plan(user_id, plan_id)`
  - `get_step_detail(user_id, plan_id, step_order)`
  - `update_step_status(user_id, plan_id, step_order, status)`

- **`LessonService`**: Responsible for lesson-specific interactions.
  - `get_lesson_detail(user_id, lesson_id)` (includes AI content generation)
  - `update_lesson_status(user_id, lesson_id, status)`
  - `get_practice_test(user_id, lesson_id)` (includes AI test generation)
  - `submit_test(user_id, lesson_id, submission)`

### 2. Refactored Services
- **`AdvisorService`**: Will now focus primarily on recommendations (`recommend` method). Logic for plan generation will move to `LearningPlanService`.

### 3. Thin Endpoints
- **`api/v1/endpoints/learning_plan.py`**: Will delegate to `LearningPlanService`.
- **`api/v1/endpoints/lessons.py`**: Will delegate to `LessonService`.

### 4. Dependency Injection
- Update `app/core/container.py` to register the new services.
- Update `app/api/deps.py` to provide helper functions for injecting the new services.

## Architecture Principles
- **Separation of Concerns**: UI/API layer should not contain business logic.
- **Single Responsibility**: Each service should have a clear, focused purpose.
- **Testability**: Moving logic to services makes it easier to unit test without HTTP overhead.

## Implementation Plan
1. Create `LearningPlanService` and `LessonService` in `app/services/`.
2. Move logic from `AdvisorService.generate_learning_plan` to `LearningPlanService`.
3. Move logic from `learning_plan.py` endpoints to `LearningPlanService`.
4. Move logic from `lessons.py` endpoints to `LessonService`.
5. Update DI configuration.
6. Refactor endpoints to use injected services.
7. Verify with existing tests.
