# Design Doc: Learning Plan Library & Advanced Generator

## 1. Overview
The goal is to expand the learning plan functionality from a single-plan system to a "Plan Library" model. Users can now generate multiple distinct plans with specific parameters (skill level, learning style, time commitment) and an optional transcript upload.

## 2. User Flow
1.  **Library View (`/plan`):**
    - Users see a vertical list of all their learning plans.
    - Each list item displays: Plan Goal, Progress %, and a "Resume" button.
    - A "Create New Plan" button is always available at the top.
2.  **Generator View (`/plan/new`):**
    - A comprehensive form collecting:
        - **Goal:** Career objective or specific topic.
        - **Interests:** Tag-based input.
        - **Skill Level:** Select (Beginner, Intermediate, Advanced).
        - **Learning Style:** Select (Visual, Practical, Theoretical).
        - **Study Time:** Number (Hours per week).
        - **Transcript:** Optional HTML file upload.
3.  **Generation:**
    - UI shows a detailed loading state while the AI sequences the path.
    - User is redirected to the active view of the new plan.

## 3. Backend & Data Models
### 3.1 Database Updates (`backend/app/infrastructure/db/models.py`)
- **`UserORM`**:
    - `default_skill_level`: String
    - `default_learning_style`: String
    - `default_study_time`: Integer
- **`LearningPlanORM`**:
    - `skill_level`: String
    - `learning_style`: String
    - `study_time`: Integer
    - `interests`: JSON (List of strings)

### 3.2 Repository Updates (`PlanRepository`)
- `get_all_plans(user_id)`: Return list of plans.
- `create_plan(...)`: Update to include new fields.

## 4. Frontend Components
### 4.1 `PlanList` (`frontend/src/components/features/plan-list.tsx`)
- A clean, list-based display of existing plans.
- Shows progress and basic metadata.

### 4.2 `LearningPlanGenerator` (`frontend/src/components/features/learning-plan-generator.tsx`)
- Replaces the simple `CreatePlanForm`.
- Integrates `react-hook-form` and file upload logic for the transcript.

### 4.3 `PlanPage` Updates
- Handles switching between the list view and the active plan view.

## 5. Verification Plan
- **Automated Tests**:
    - Verify multiple plans can be saved and retrieved.
    - Verify the transcript parser output is correctly integrated into plan generation context.
- **Manual Verification**:
    - Create three plans with different styles/levels.
    - Upload an HTML transcript and verify the "prior knowledge" reflected in the generated steps.
