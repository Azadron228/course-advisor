# Admin Course Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a complete admin interface for course management, including listing, creating, editing, and uploading materials.

**Architecture:** Dedicated admin pages following the project's "Intelligent Learning Framework" design system. Uses a centralized `useAdminCourses` hook for data management and shared form components for consistency.

**Tech Stack:** FastAPI (Backend), Next.js 15 (Frontend), TanStack Query, TailwindCSS 4, Lucide Icons.

---

### Task 1: Backend - Course Creation Endpoint

**Files:**
- Modify: `backend/app/api/v1/endpoints/admin.py`
- Test: `backend/tests/test_admin_courses.py` (Create new)

- [ ] **Step 1: Write test for course creation**

```python
def test_create_course_admin(client, admin_token_headers):
    data = {
        "id": "CS101_NEW",
        "subject_name": "Intro to Plan Writing",
        "credits": 3.0,
        "description": "Learn to write implementation plans.",
        "skills_taught": ["Planning", "Design"],
        "difficulty": 0.5,
        "workload": 0.5
    }
    response = client.post("/api/v1/admin/courses", json=data, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "CS101_NEW"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_admin_courses.py`
Expected: 404 Not Found (endpoint missing)

- [ ] **Step 3: Implement `POST /admin/courses`**

```python
@router.post("/courses", response_model=CoursePublic)
async def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
):
    course_repo = CourseRepository(db)
    if course_repo.get_by_id(course_in.id):
        raise HTTPException(status_code=400, detail="Course ID already exists")

    # Generate initial embedding
    embedding = get_embedding(course_in.description)
    
    # Create CourseORM
    from app.infrastructure.db.models import CourseORM
    db_course = CourseORM(
        **course_in.model_dump(),
        embedding=embedding
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
```

- [ ] **Step 4: Run test to verify it passes**

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/endpoints/admin.py
git commit -m "feat(admin): add course creation endpoint"
```

---

### Task 2: Frontend - Admin Courses Hook

**Files:**
- Create: `frontend/src/hooks/use-admin-courses.ts`

- [ ] **Step 1: Implement `useAdminCourses` hook**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface Course {
  id: string;
  subject_name: str;
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

  const createMutation = useMutation({
    mutationFn: (data: Omit<Course, 'materials_content'>) => apiClient.post<Course>('/admin/courses', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] }),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Course> }) => apiClient.put<Course>(`/admin/courses/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/admin/courses/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] }),
  });

  const uploadMaterialsMutation = useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post<Course>(`/admin/courses/${id}/materials`, formData);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] }),
  });

  return {
    courses: coursesQuery.data || [],
    isLoading: coursesQuery.isLoading,
    createCourse: createMutation.mutateAsync,
    updateCourse: updateMutation.mutateAsync,
    deleteCourse: deleteMutation.mutateAsync,
    uploadMaterials: uploadMaterialsMutation.mutateAsync,
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/use-admin-courses.ts
git commit -m "feat(admin): add useAdminCourses hook"
```

---

### Task 3: Frontend - Admin Navigation

**Files:**
- Modify: `frontend/src/components/admin/admin-sidebar.tsx`

- [ ] **Step 1: Add Courses to `navItems`**

```typescript
import { Users, LayoutDashboard, Settings, BookOpen } from 'lucide-react';
// ...
const navItems = [
  { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { name: 'Courses', href: '/admin/courses', icon: BookOpen },
  { name: 'Users', href: '/admin/users', icon: Users },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
];
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/admin/admin-sidebar.tsx
git commit -m "feat(admin): add courses link to sidebar"
```

---

### Task 4: Frontend - Course List Page

**Files:**
- Create: `frontend/src/app/[locale]/admin/courses/page.tsx`

- [ ] **Step 1: Implement Course List Page**

```tsx
'use client';

import { useAdminCourses } from '@/hooks/use-admin-courses';
import Link from 'next/link';
import { Plus, Book, Trash2, Edit } from 'lucide-react';

export default function AdminCourseListPage() {
  const { courses, isLoading, deleteCourse } = useAdminCourses();

  if (isLoading) return <div>Loading courses...</div>;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold font-lexend text-slate-900">Course Management</h1>
        <Link 
          href="/admin/courses/new"
          className="bg-primary text-white px-6 py-3 rounded-xl shadow-lg shadow-primary/20 flex items-center hover:bg-primary-dark transition-all"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add New Course
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div key={course.id} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-all group">
            <div className="flex justify-between items-start mb-4">
              <div className="p-3 bg-primary/5 rounded-xl">
                <Book className="w-6 h-6 text-primary" />
              </div>
              <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Link href={`/admin/courses/${course.id}`} className="p-2 text-slate-400 hover:text-primary rounded-lg hover:bg-slate-100">
                  <Edit className="w-4 h-4" />
                </Link>
                <button 
                  onClick={() => confirm('Delete?') && deleteCourse(course.id)}
                  className="p-2 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            <h3 className="text-lg font-bold text-slate-900 font-lexend mb-1">{course.subject_name}</h3>
            <p className="text-sm text-slate-500 mb-4">{course.id} • {course.credits} Credits</p>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-500 mb-1">
                  <span>Difficulty</span>
                  <span>{Math.round(course.difficulty * 100)}%</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${course.difficulty * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/admin/courses/page.tsx
git commit -m "feat(admin): implement course list page"
```

---

### Task 5: Frontend - Course Form Component

**Files:**
- Create: `frontend/src/components/admin/course-form.tsx`

- [ ] **Step 1: Implement `CourseForm`**

```tsx
'use client';

import { useState } from 'react';
import { Course } from '@/hooks/use-admin-courses';

interface CourseFormProps {
  initialData?: Partial<Course>;
  onSubmit: (data: any) => Promise<void>;
  isSubmitting: boolean;
  isEdit?: boolean;
}

export function CourseForm({ initialData, onSubmit, isSubmitting, isEdit }: CourseFormProps) {
  const [formData, setFormData] = useState({
    id: initialData?.id || '',
    subject_name: initialData?.subject_name || '',
    credits: initialData?.credits || 3,
    description: initialData?.description || '',
    skills_taught: initialData?.skills_taught?.join(', ') || '',
    difficulty: initialData?.difficulty || 0.5,
    workload: initialData?.workload || 0.5,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const skills = formData.skills_taught.split(',').map(s => s.trim()).filter(Boolean);
    onSubmit({ ...formData, skills_taught: skills });
  };

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4">
          <h2 className="text-lg font-bold font-lexend text-slate-900">General Information</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Course ID</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 disabled:bg-slate-50 outline-none"
              value={formData.id}
              disabled={isEdit}
              onChange={e => setFormData({ ...formData, id: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Subject Name</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 outline-none"
              value={formData.subject_name}
              onChange={e => setFormData({ ...formData, subject_name: e.target.value })}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Credits</label>
              <input
                type="number"
                step="0.5"
                className="w-full px-4 py-2 rounded-lg border border-slate-200 outline-none"
                value={formData.credits}
                onChange={e => setFormData({ ...formData, credits: parseFloat(e.target.value) })}
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea
              className="w-full px-4 py-2 rounded-lg border border-slate-200 h-32 outline-none"
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              required
            />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-6">
          <h2 className="text-lg font-bold font-lexend text-slate-900">Metadata & Skills</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Skills Taught (comma separated)</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 outline-none"
              value={formData.skills_taught}
              onChange={e => setFormData({ ...formData, skills_taught: e.target.value })}
              placeholder="React, TypeScript, Testing..."
            />
          </div>
          
          <div>
            <div className="flex justify-between text-sm font-medium text-slate-700 mb-2">
              <span>Difficulty</span>
              <span>{Math.round(formData.difficulty * 100)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              className="w-full accent-primary"
              value={formData.difficulty}
              onChange={e => setFormData({ ...formData, difficulty: parseFloat(e.target.value) })}
            />
          </div>

          <div>
            <div className="flex justify-between text-sm font-medium text-slate-700 mb-2">
              <span>Workload</span>
              <span>{Math.round(formData.workload * 100)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              className="w-full accent-primary"
              value={formData.workload}
              onChange={e => setFormData({ ...formData, workload: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-white font-bold py-4 rounded-2xl shadow-lg shadow-primary/20 hover:bg-primary-dark transition-all disabled:opacity-50"
        >
          {isSubmitting ? 'Saving...' : (isEdit ? 'Update Course' : 'Create Course')}
        </button>
      </div>
    </form>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/admin/course-form.tsx
git commit -m "feat(admin): add shared course form component"
```

---

### Task 6: Frontend - Create Course Page

**Files:**
- Create: `frontend/src/app/[locale]/admin/courses/new/page.tsx`

- [ ] **Step 1: Implement Create Page**

```tsx
'use client';

import { CourseForm } from '@/components/admin/course-form';
import { useAdminCourses } from '@/hooks/use-admin-courses';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewCoursePage() {
  const { createCourse } = useAdminCourses();
  const router = useRouter();

  const handleCreate = async (data: any) => {
    try {
      await createCourse(data);
      router.push('/admin/courses');
    } catch (e) {
      alert('Failed to create course');
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link href="/admin/courses" className="flex items-center text-slate-500 hover:text-slate-700 mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Courses
      </Link>
      <h1 className="text-3xl font-bold font-lexend text-slate-900 mb-8">Add New Course</h1>
      <CourseForm onSubmit={handleCreate} isSubmitting={false} />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/admin/courses/new/page.tsx
git commit -m "feat(admin): implement create course page"
```

---

### Task 7: Frontend - Edit Course Page & Material Upload

**Files:**
- Create: `frontend/src/app/[locale]/admin/courses/[id]/page.tsx`

- [ ] **Step 1: Implement Edit Page with Material Upload**

```tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useAdminCourses } from '@/hooks/use-admin-courses';
import { CourseForm } from '@/components/admin/course-form';
import { ArrowLeft, Upload, FileText, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

export default function EditCoursePage() {
  const { id } = useParams();
  const { courses, updateCourse, uploadMaterials } = useAdminCourses();
  const router = useRouter();
  const [uploading, setUploading] = useState(false);

  const course = courses.find(c => c.id === id);

  if (!course) return <div>Course not found</div>;

  const handleUpdate = async (data: any) => {
    await updateCourse({ id: id as string, data });
    router.push('/admin/courses');
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadMaterials({ id: id as string, file });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link href="/admin/courses" className="flex items-center text-slate-500 hover:text-slate-700 mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Courses
      </Link>
      
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold font-lexend text-slate-900">Edit Course: {course.id}</h1>
      </div>

      <div className="space-y-8">
        <div className="bg-primary/5 p-6 rounded-2xl border border-primary/10 flex items-center justify-between">
          <div className="flex items-center">
            <div className="p-3 bg-white rounded-xl shadow-sm mr-4">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900">Educational Materials</h3>
              <p className="text-sm text-slate-500">
                {course.materials_content ? 'Syllabus analyzed for RAG recommendations' : 'Upload PDF/Txt for better AI recommendations'}
              </p>
            </div>
          </div>
          <label className="bg-white border border-slate-200 px-4 py-2 rounded-lg cursor-pointer hover:bg-slate-50 transition-all flex items-center">
            <Upload className="w-4 h-4 mr-2 text-slate-400" />
            {uploading ? 'Uploading...' : 'Upload File'}
            <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.txt" />
          </label>
        </div>

        <CourseForm 
          initialData={course} 
          onSubmit={handleUpdate} 
          isSubmitting={false} 
          isEdit 
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/admin/courses/[id]/page.tsx
git commit -m "feat(admin): implement edit course page with material upload"
```

---

### Task 8: Verification

- [ ] **Step 1: Verify all tasks are complete**
- [ ] **Step 2: Run backend tests**
- [ ] **Step 3: Manually verify in UI**
