# Design Doc: Course Materials Side Drawer

## 1. Overview
The goal is to allow users to view detailed course materials directly from their Learning Plan. Internal courses will open in a side drawer with Markdown rendering, while external resources will link directly to their source.

## 2. User Flow
1.  **Trigger:** User navigates to their active plan on `/plan`.
2.  **Interaction:** User clicks "View Resource" on a specific learning path step.
3.  **Branching Logic:**
    - If the step is **external**, it opens the external URL in a new tab.
    - If the step is **internal** (linked to an internal course ID), it opens a side drawer.
4.  **Drawer Content:**
    - The drawer fetches the specific course data.
    - Displays Course Title, Description, and the full `materials_content`.
    - Materials are rendered as Markdown for readability.

## 3. Backend Implementation
### 3.1 New Endpoint (`GET /api/v1/courses/{course_id}`)
- **Location:** `backend/app/api/v1/endpoints/courses.py`
- **Security:** Requires active user authentication.
- **Functionality:** Retrieves a course by ID from the `CourseRepository`.

### 3.2 Router Registration
- Register the new `courses` router in `backend/app/api/router.py`.

### 3.3 Data Seeding (`backend/seed.py`)
- Update the default courses to include dummy Markdown content in the `materials_content` field.

## 4. Frontend Implementation
### 4.1 `CourseDrawer` Component
- **Location:** `frontend/src/components/shared/course-drawer.tsx`
- **Props:** `courseId: string | null`, `onClose: () => void`.
- **Logic:**
    - Uses a slide-out animation (Tailwind + Framer Motion or Headless UI).
    - Fetches data from `/api/v1/courses/{course_id}`.
    - Uses `react-markdown` to render the content.

### 4.2 `PlanStepper` Integration
- Add state to track the `selectedCourseId` for the drawer.
- Update the "View Resource" button logic to handle the internal/external split.

## 5. Verification Plan
- **Backend Tests:** Verify the `/courses/{id}` endpoint returns correct data and handles 404s.
- **Frontend Tests:**
    - Verify "View Resource" opens the drawer for internal courses.
    - Verify Markdown renders correctly within the drawer.
- **Manual Verification:** Seed the database, generate a plan, and open the drawer for "CS401".
