# Design Spec: Admin Course Management

**Topic:** Implementation of dedicated admin pages for course management (CRUD).
**Date:** 2026-04-29
**Status:** Draft

## 1. Overview
The goal is to provide administrators with a robust interface for managing the course catalog. This includes listing, creating, editing, and deleting courses, as well as uploading educational materials (PDF/Text) for RAG-based analysis.

## 2. Architecture

### 2.1 Backend (Python/FastAPI)
- **New Endpoint:** `POST /admin/courses`
    - Input: `CourseCreate` schema.
    - Logic: Validates ID uniqueness, generates 1536d embedding for `description`, and persists to `courses` table.
- **Consistency:** Ensure `GET /admin/courses`, `PUT /admin/courses/{id}`, and `DELETE /admin/courses/{id}` are fully functional and protected by `get_current_admin_user`.

### 2.2 Frontend (Next.js/React)
- **Data Layer:** `useAdminCourses` hook using TanStack Query.
    - Query Key: `['admin', 'courses']`.
    - Mutations for CRUD and material uploads.
- **Routing:**
    - `/admin/courses`: List view.
    - `/admin/courses/new`: Creation page.
    - `/admin/courses/[id]`: Edit page with material management.

## 3. UI Design (Intelligent Learning Framework)

### 3.1 Course List Page
- **Layout:** Grid of cards (Level 1 elevation).
- **Cards:** Display `subject_name`, `credits`, `difficulty` (as a progress bar), and `workload`.
- **Actions:** Prominent "Edit" and "Delete" buttons on each card.

### 3.2 Course Form (Shared Component)
- **Design:** Two-column layout on large screens.
- **Fields:**
    - General: Subject, ID (String), Credits (Float), Description (Textarea).
    - Metadata: Difficulty (0-1), Workload (0-1), Skills Taught (Comma-separated text).
- **Material Management (Edit Only):**
    - File upload area for `.pdf` and `.txt` files.
    - Display current material status (e.g., "Syllabus uploaded").

## 4. Design Standards
- **Typography:** Lexend for headings, Inter for body copy.
- **Colors:** Primary Indigo (#4F46E5), Success Green (#10B981).
- **Shapes:** 0.5rem (8px) roundness for inputs/buttons, 1rem (16px) for cards.

## 5. Security & Validation
- **Auth:** All endpoints required `is_admin` flag.
- **Validation:** Pydantic on backend, Zod on frontend.
- **Embeddings:** Automatically recalculated when the description or materials change.

## 6. Implementation Plan Preview
1. Implement `POST /admin/courses` in backend.
2. Create `useAdminCourses` hook in frontend.
3. Scaffold `/admin/courses/` page structure.
4. Implement `AdminCourseList` and `CourseForm` components.
5. Add material upload functionality.
6. Verify with E2E tests.
