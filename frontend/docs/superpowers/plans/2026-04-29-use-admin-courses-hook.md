# Admin Courses Hook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `useAdminCourses` hook for managing courses in the admin interface.

**Architecture:** TanStack Query hook that encapsulates CRUD operations for courses. Uses `apiClient` for API calls and invalidates the `['admin', 'courses']` query key on success.

**Tech Stack:** React, TanStack Query, TypeScript.

---

### Task 1: Create useAdminCourses Hook

**Files:**
- Create: `src/hooks/use-admin-courses.ts`

- [ ] **Step 1: Implement the hook with Course interface and operations**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

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

export function useAdminCourses() {
  const queryClient = useQueryClient();

  const coursesQuery = useQuery({
    queryKey: ['admin', 'courses'],
    queryFn: () => apiClient.get<Course[]>('/admin/courses'),
  });

  const createCourseMutation = useMutation({
    mutationFn: (data: Omit<Course, 'materials_content'>) => 
      apiClient.post<Course>('/admin/courses', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const updateCourseMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Course> }) =>
      apiClient.put<Course>(`/admin/courses/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const deleteCourseMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/admin/courses/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  const uploadMaterialsMutation = useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post<Course>(`/admin/courses/${id}/materials`, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
    },
  });

  return {
    courses: coursesQuery.data || [],
    isLoading: coursesQuery.isLoading,
    error: coursesQuery.error,
    createCourse: createCourseMutation.mutateAsync,
    updateCourse: updateCourseMutation.mutateAsync,
    deleteCourse: deleteCourseMutation.mutateAsync,
    uploadMaterials: uploadMaterialsMutation.mutateAsync,
  };
}
```

- [ ] **Step 2: Verify syntax with TypeScript compiler**

Run: `npx tsc src/hooks/use-admin-courses.ts --noEmit --esModuleInterop --skipLibCheck --target esnext --moduleResolution node --jsx react-jsx`
Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add src/hooks/use-admin-courses.ts
git commit -m "feat(admin): add useAdminCourses hook"
```
