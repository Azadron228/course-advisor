# Multi-File Course Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement multi-file course materials management with status tracking and individual deletion, matching the Stitch project UI/UX.

**Architecture:**
- **Backend:** Add `CourseMaterialORM`, update `CourseORM`. Add materials CRUD endpoints. Refactor RAG logic to use aggregated materials.
- **Frontend:** Update `useAdminCourses` hook and `EditCoursePage`. Implement `MaterialsList` component.

---

### Task 1: Backend Models and Repositories

- [x] **Step 1: Update `backend/app/infrastructure/db/models.py`**
    - Add `CourseMaterialORM`.
    - Update `CourseORM` relationship.
- [x] **Step 2: Update `backend/app/domain/catalog/entities.py`**
    - Add `CourseMaterial` dataclass.
    - Update `Course` dataclass to include `materials: List[CourseMaterial]`.
- [x] **Step 3: Update `backend/app/infrastructure/db/repositories/course_repository.py`**
    - Implement `get_materials(course_id)`.
    - Implement `add_material(material)`.
    - Implement `delete_material(material_id)`.
    - Update `save()` to handle materials relationship (or at least preserve it).

---

### Task 2: API Schemas and Endpoints

- [x] **Step 1: Add schemas in `backend/app/api/v1/schemas/course.py`**
    - `CourseMaterialPublic`.
- [x] **Step 2: Update `backend/app/api/v1/endpoints/admin.py`**
    - Update `upload_course_materials` to create `CourseMaterialORM`.
    - Add `DELETE /courses/{course_id}/materials/{material_id}`.
    - Add `GET /courses/{course_id}/materials`.
- [x] **Step 3: Update `backend/app/api/v1/endpoints/courses.py`**
    - Ensure `GET /courses/{id}` returns materials.

---

### Task 3: AI Logic Refactor

- [x] **Step 1: Update RAG aggregation in `backend/app/services/advisor_service.py`**
    - When fetching courses, ensure materials are loaded and concatenated for the agent.

---

### Task 4: Frontend Implementation

- [x] **Step 1: Update `frontend/src/hooks/use-admin-courses.ts`**
    - Update `Course` interface.
    - Add `deleteMaterial` mutation.
    - Ensure `uploadMaterials` works with the new flow.
- [x] **Step 2: Implement Materials UI in `frontend/src/app/[locale]/admin/courses/[id]/page.tsx`**
    - Display a list of uploaded files with status badges.
    - Implement delete action.
    - Polish the upload zone styling.

---

### Task 5: Verification

- [x] **Step 1: Run backend tests**
- [ ] **Step 2: Manually verify multi-file upload and deletion in UI**
- [ ] **Step 3: Verify AI recommendations still use materials content**
