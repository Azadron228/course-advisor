# Design Doc: Removing Course Parameters and Refactoring ID

## Overview
Simplify the course management and learning path by removing 'difficulty', 'workload', and 'credits' from the course catalog. Additionally, refactor the course identifier from a string (e.g., "CS101") to an internal autoincrementing integer.

## Changes

### 1. Database Schema
- **Table `courses`**:
    - Drop columns: `difficulty`, `workload`, `credits`.
    - Change `id` from `String` to `Integer` (Autoincrement, Primary Key).
- **Table `user_transcripts`**:
    - **No changes** (Keep `credits` as requested).

### 2. Backend Implementation
- **Models (`app/infrastructure/db/models.py`)**:
    - Update `CourseORM` to remove the columns and change `id` type.
- **Domain Entities (`app/domain/catalog/entities.py`, `app/domain/recommendation/entities.py`)**:
    - Update `Course` entity to remove `credits`, `difficulty`, `workload`.
    - Update `UserPreference` to remove `target_difficulty`, `max_workload`.
- **API Schemas (`app/api/v1/schemas/course.py`, `app/api/v1/schemas/recommendations.py`)**:
    - Update `CourseSchema`, `CourseCreate`, `CourseUpdate` to remove fields and change `id` to `int`.
    - Update `UserPreferenceSchema` to remove fields.
    - Update `RecommendationResult` to use `int` for `course_id`.
- **Scoring Logic (`app/domain/recommendation/scoring.py`)**:
    - Remove difficulty and workload penalties from `calculate_preference_score`.
- **Repositories & Services**:
    - Update `CourseRepository` and `AdvisorService` to align with new entities and schemas.
- **Seed Data (`seed.py`)**:
    - Update to remove the fields from course definitions.

### 3. Frontend Implementation
- **Admin UI (`admin/courses/page.tsx`, `course-form.tsx`)**:
    - Remove "Difficulty", "Workload", and "Credits" fields.
    - Remove the human-readable "ID" field from display and forms.
- **Recommendation UI**:
    - Remove any display of the removed fields in recommendation cards or score breakdowns.
- **Localization**:
    - Remove unused keys from `en.json` and `ru.json`.

### 4. Migration Plan
- Create an Alembic migration that:
    1.  Drops the columns.
    2.  Drops the old primary key `id` (string).
    3.  Adds a new `id` column as `SERIAL` (autoincrementing int) and sets it as primary key.
    - *Note: Since this is a prototype, we don't need to preserve existing data relationships if they were using the old string ID as a foreign key, but we should be careful if there are any.*

## Success Criteria
- Courses can be managed (CRUD) without difficulty, workload, or credits.
- Recommendations work correctly without these parameters.
- The UI is cleaner and focused on subject name and description.
- All tests pass.
