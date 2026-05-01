# Multi-File Course Materials Management Design

## 1. Overview
The current system supports only a single course material text blob per course. To provide a professional admin experience (matching the Stitch project), we need to support multiple uploaded files, track their status, and allow individual management (listing/deletion).

## 2. Architecture

### 2.1 Database Changes
- **New Model:** `CourseMaterialORM`
    - `id`: Integer (PK)
    - `course_id`: Integer (FK to courses.id)
    - `filename`: String (original filename)
    - `content`: Text (extracted content)
    - `status`: String ("pending", "analyzed", "error")
    - `created_at`: String (ISO format)

- **CourseORM Update:**
    - Remove `materials_content` (migration logic should migrate existing content to a "Legacy Materials" entry).
    - Add relationship to `CourseMaterialORM`.

### 2.2 API Endpoints (Admin)
- `GET /admin/courses/{course_id}/materials`: List all materials for a course.
- `POST /admin/courses/{course_id}/materials`: Upload a new material (multipart/form-data).
- `DELETE /admin/courses/{course_id}/materials/{material_id}`: Remove a material.

### 2.3 Domain Entities & Schemas
- `CourseMaterial` domain entity.
- `CourseMaterialPublic` and `CourseMaterialCreate` schemas.

### 2.4 AI Integration
- The aggregated `materials_content` for RAG should now be a concatenation of all "analyzed" materials for that course.

## 3. Frontend UI
- **Materials Section:** A dedicated card in the Course Edit page.
- **Upload Zone:** A dashed-border dropzone or prominent button.
- **Materials List:**
    - Icon based on file type (PDF/TXT).
    - Filename and size/date.
    - Status badge:
        - `Analyzed`: Success (Green)
        - `Pending`: In progress (Orange)
        - `Error`: Failure (Red)
    - Trash icon for deletion.

## 4. Design System Alignment
- Follow "Intelligent Learning Framework":
    - Primary: Indigo #4F46E5
    - Font: Lexend (headings), Inter (body)
    - Roundness: 16px (cards), 8px (items)
    - Elevation: Level 1 shadow.

## 5. Verification Plan
- **Backend:** Unit tests for upload/delete/list materials.
- **Frontend:** Visual verification of the materials list and upload workflow.
- **AI:** Ensure RAG still works by verifying embeddings are updated when materials change.
