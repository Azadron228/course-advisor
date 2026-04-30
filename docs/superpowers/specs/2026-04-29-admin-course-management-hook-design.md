# Design Spec: Frontend Admin Courses Hook

**Topic:** Implementation of `useAdminCourses` TanStack Query hook.
**Date:** 2026-04-29
**Status:** Approved

## 1. Overview
The `useAdminCourses` hook provides a centralized interface for administrative course management operations. it encapsulates data fetching and mutation logic using TanStack Query, interacting with the `/admin/courses` API endpoints.

## 2. Data Model

```typescript
export interface Course {
  id: string;
  subject_name: string;
  credits: number;
  description: string;
  skills_taught: string[];
  difficulty: number;
  workload: number;
  materials_content?: string;
}
```

## 3. Hook Functionality

### 3.1 Queries
- **`courses`**: Fetches all courses.
  - Endpoint: `GET /admin/courses`
  - Query Key: `['admin', 'courses']`

### 3.2 Mutations
- **`createCourse`**: Creates a new course.
  - Endpoint: `POST /admin/courses`
  - Payload: `Omit<Course, 'materials_content'>`
- **`updateCourse`**: Updates an existing course.
  - Endpoint: `PUT /admin/courses/${id}`
  - Payload: `Partial<Course>`
- **`deleteCourse`**: Deletes a course.
  - Endpoint: `DELETE /admin/courses/${id}`
- **`uploadMaterials`**: Uploads course materials.
  - Endpoint: `POST /admin/courses/${id}/materials`
  - Payload: `FormData` (containing `file`)

### 3.3 Cache Invalidation
Upon success of any mutation, the `['admin', 'courses']` query key will be invalidated to trigger a refetch and keep the UI in sync.

## 4. Implementation Details
- Uses `apiClient` from `@/lib/api-client`.
- Leverages `useQuery`, `useMutation`, and `useQueryClient` from `@tanstack/react-query`.
- Pattern follows `src/hooks/use-users.ts`.
