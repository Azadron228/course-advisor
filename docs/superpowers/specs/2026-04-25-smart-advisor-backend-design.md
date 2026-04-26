# Design Doc: Smart Advisor Backend Refactor

## 1. Overview
The goal is to transition the backend from a mocked state to a fully functional "Smart Advisor" that supports the dynamic frontend prototype. This includes persistent user profiles, AI-generated learning plans, and an interactive skill map.

## 2. Data Models & Schema
### 2.1 Extended User Profile
- **`users` Table (Existing + New):**
    - `career_goal`: Text (e.g., "Full Stack Developer")
    - `onboarding_completed`: Boolean
- **`user_skills` Table (New):**
    - `user_id`: ForeignKey(users.id)
    - `skill_name`: String
    - `mastery_level`: Integer (0-100)
    - `category`: String (e.g., "Frontend", "AI")
- **`user_transcript` Table (New):**
    - `user_id`: ForeignKey(users.id)
    - `subject_name`: String
    - `credits`: Float
    - `mark`: Float
- **`learning_plans` Table (New):**
    - `user_id`: ForeignKey(users.id)
    - `goal`: String
    - `steps`: JSON (List of LearningPathStep entities)
    - `is_active`: Boolean

## 3. Core Services
### 3.1 Advisor Service Enhancement
- **Dynamic Plan Generation:** Uses LLM (Gemini) to analyze the user's transcript and skills against their career goal to generate a sequenced list of recommended courses and learning steps.
- **Skill Gap Analysis:** Compares the user's current `user_skills` against the required skill profile for their `career_goal`.
- **Skill Map Derivation:** Generates a graph structure (`SkillNode`s) for the frontend "Interactive Skill Map".

### 3.2 AI Agent Integration
- **Contextual Awareness:** The agent in `/chat` will have access to the user's persistent profile and the current active learning plan.
- **Tools:** The agent will be able to query the `CourseRepository` to provide specific, data-backed recommendations.

## 4. API Endpoints
### 4.1 Auth & Users
- `GET /api/v1/users/me`: Fetch own profile, skills, and transcript.
- `PATCH /api/v1/users/me`: Update profile details.
- `POST /api/v1/auth/onboarding`: Specialized endpoint to set initial skills and goals.

### 4.2 Learning Plan
- `GET /api/v1/learning-plan`: Fetch current plan.
- `POST /api/v1/learning-plan/generate`: AI-driven generation of a new plan.
- `PATCH /api/v1/learning-plan/steps/{step_id}`: Update step status (e.g., mark as completed).

### 4.3 Skills
- `GET /api/v1/skills/map`: Fetch the dynamic skill map.

### 4.4 Dashboard
- `GET /api/v1/dashboard`: Unified summary for the navigation hub (active plan title, progress percentage, welcome message).

## 5. Implementation Strategy
1.  **Database Migration:** Use Alembic to add new tables and columns.
2.  **Domain Entities:** Update entities in `app/domain/` to include new fields.
3.  **Repository Layer:** Implement `UserSkillRepository` and `LearningPlanRepository`.
4.  **Service Layer:** Expand `AdvisorService` with AI generation logic.
5.  **API Layer:** Implement/Update endpoints and Pydantic schemas.
6.  **Verification:** Add unit tests for AI generation and integration tests for the new endpoints.
