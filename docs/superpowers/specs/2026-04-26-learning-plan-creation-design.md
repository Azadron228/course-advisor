# Design Doc: Learning Plan Creation & Onboarding Consolidation

## 1. Overview
The goal is to streamline the user experience by removing the global onboarding modal and integrating its data collection (name, goal, interests) into a unified "Create Learning Plan" flow on the `/plan` page.

## 2. User Flow
1.  **Entry:** User navigates to the `/plan` page.
2.  **State Check:** 
    - If an active plan exists, show the `PlanStepper`.
    - If no active plan exists, show the `CreatePlanForm`.
3.  **Creation Form:**
    - Field 1: **Full Name** (pre-filled if already set).
    - Field 2: **Career Goal** (textarea).
    - Field 3: **Interests/Skills** (tag-based multi-select).
4.  **Submission:**
    - User clicks "Generate My Learning Path".
    - UI shows a loading state (e.g., "AI is drafting your personalized path...").
5.  **Completion:**
    - Backend updates the user profile and generates the plan.
    - Page revalidates and displays the new `PlanStepper`.

## 3. Components
### 3.1 `CreatePlanForm` (New)
- **Location:** `frontend/src/components/features/create-plan-form.tsx`
- **Features:** 
    - Form validation using Zod.
    - Tag input for interests.
    - Integration with a new `generatePlan` server action.

### 3.2 `PlanPage` (Update)
- **Location:** `frontend/src/app/[locale]/plan/page.tsx`
- **Logic:** Conditional rendering based on the presence of a learning plan.

## 4. API & Actions
### 4.1 `generatePlan` Server Action (New)
- **Location:** `frontend/src/app/[locale]/plan/actions.ts`
- **Responsibilities:**
    1.  Call `PATCH /api/v1/users/me` to update `full_name`, `career_goal`, and set `onboarding_completed: true`.
    2.  Call `POST /api/v1/learning-plan/generate` to trigger AI generation.
    3.  Call `revalidatePath('/plan')`.

## 5. Cleanup & Removal
- **`OnboardingWizard` Removal:**
    - Delete `frontend/src/components/features/onboarding-wizard.tsx`.
    - Remove imports and usage in `frontend/src/components/shared/main-layout.tsx`.
- **Dashboard Cleanup:**
    - Remove the "Finish your profile setup!" banner from `frontend/src/app/[locale]/dashboard/page.tsx`.

## 6. Verification Plan
- **Automated Tests:**
    - Verify `PlanPage` renders the form when no plan is present.
    - Verify the server action correctly chains the profile update and generation calls.
- **Manual Verification:**
    - Create a new user, navigate to `/plan`, and verify the end-to-end creation flow.
    - Verify the onboarding modal no longer appears on other pages.
