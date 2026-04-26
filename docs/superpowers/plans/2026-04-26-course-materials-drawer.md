# Course Materials Side Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a side drawer to display rich Markdown course materials for internal courses, while maintaining direct links for external resources.

**Architecture:**
- **Backend:** Add a public authenticated endpoint `GET /courses/{id}` to fetch course details. Update seed data with Markdown content.
- **Frontend:** Create a reusable `CourseDrawer` component using Tailwind and Headless UI (or similar). Integrate it into `PlanStepper` to intercept "View Resource" clicks for internal IDs.

**Tech Stack:** FastAPI (Backend), Next.js, Tailwind CSS, Headless UI (Transitions), `react-markdown` (Frontend).

---

### Task 1: Backend Course API & Seed Data

**Files:**
- Create: `backend/app/api/v1/endpoints/courses.py`
- Modify: `backend/app/api/router.py`
- Modify: `backend/seed.py`

- [ ] **Step 1: Create the courses endpoint**

```python
# backend/app/api/v1/endpoints/courses.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user, get_service
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.api.v1.schemas.course import CoursePublic
from app.domain.identity.entities import User

router = APIRouter()

@router.get("/{course_id}", response_model=CoursePublic)
async def get_course_by_id(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    course_repo: CourseRepository = Depends(get_service(CourseRepository))
):
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
```

- [ ] **Step 2: Register the router**

```python
# backend/app/api/router.py
# ... add at bottom
from app.api.v1.endpoints import courses
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
```

- [ ] **Step 3: Update seed data with Markdown**

```python
# backend/seed.py
# Update the COURSES list to include materials_content for at least one course (e.g., CS401)
COURSES = [
    {
        "id": "CS401",
        "subject_name": "Artificial Intelligence",
        "credits": 6.0,
        "description": "Comprehensive introduction to AI...",
        "skills_taught": ["Python", "Machine Learning", "AI", "Algorithms"],
        "difficulty": 0.8,
        "workload": 0.7,
        "materials_content": """
# Introduction to Artificial Intelligence
Welcome to CS401. This course covers:
- **Search Algorithms**: A*, BFS, DFS.
- **Machine Learning**: Linear Regression to Neural Nets.
- **Ethics**: The impact of AI on society.

## Recommended Reading
Check out the official documentation for [Scikit-Learn](https://scikit-learn.org).
        """
    },
    # ... update others with similar structure
]

# Ensure the loop in seed() assigns materials_content:
# course = CourseORM(..., materials_content=c.get("materials_content"))
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/endpoints/courses.py backend/app/api/router.py backend/seed.py
git commit -m "feat(backend): add public course endpoint and rich seed data"
```

---

### Task 2: Frontend Dependencies & `CourseDrawer` Component

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/components/shared/course-drawer.tsx`

- [ ] **Step 1: Install `react-markdown`**

Run: `cd frontend && npm install react-markdown`

- [ ] **Step 2: Implement the `CourseDrawer` component**

```tsx
'use client';

import { useState, useEffect } from 'react';
import { X, Loader2, BookOpen, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { apiClient } from '@/lib/api-client';
import { Course } from '@/app/api/v1/schemas/course'; // Ensure this matches your export

interface CourseDrawerProps {
  courseId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function CourseDrawer({ courseId, isOpen, onClose }: CourseDrawerProps) {
  const [course, setCourse] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && courseId) {
      setIsLoading(true);
      setError(null);
      apiClient.get(`/courses/${courseId}`)
        .then(res => setCourse(res))
        .catch(err => setError('Failed to load course materials'))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, courseId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" onClick={onClose} />
      
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-2xl transform transition-all animate-in slide-in-from-right duration-300">
          <div className="flex h-full flex-col bg-white shadow-2xl border-l border-slate-200">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-slate-50/50">
              <div className="flex items-center gap-3">
                <div className="bg-indigo-100 p-2 rounded-lg text-indigo-600">
                  <BookOpen className="w-5 h-5" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">Course Materials</h2>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-8">
              {isLoading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-3">
                  <Loader2 className="w-8 h-8 animate-spin" />
                  <p className="font-medium">Loading materials...</p>
                </div>
              ) : error ? (
                <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-100">
                  {error}
                </div>
              ) : course && (
                <div className="space-y-8">
                  <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 mb-4">{course.subject_name}</h1>
                    <p className="text-lg text-slate-600 leading-relaxed">{course.description}</p>
                  </div>

                  <div className="prose prose-slate max-w-none border-t border-slate-100 pt-8">
                    {course.materials_content ? (
                      <ReactMarkdown>{course.materials_content}</ReactMarkdown>
                    ) : (
                      <p className="italic text-slate-400">No specific materials provided for this course yet.</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/src/components/shared/course-drawer.tsx
git commit -m "feat(frontend): add CourseDrawer component with Markdown support"
```

---

### Task 3: `PlanStepper` Integration

**Files:**
- Modify: `frontend/src/components/features/plan-stepper.tsx`

- [ ] **Step 1: Integrate drawer state and logic**

```tsx
// frontend/src/components/features/plan-stepper.tsx
// ... imports
import { CourseDrawer } from '@/components/shared/course-drawer';

export function PlanStepper({ plan }: PlanStepperProps) {
  // ... existing state
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleViewResource = (step: LearningPathStep) => {
    if (step.is_external && step.resource_id) {
       window.open(step.resource_id, '_blank');
    } else if (step.resource_id) {
       setSelectedCourseId(step.resource_id);
       setIsDrawerOpen(true);
    }
  };

  return (
    <>
      <div className="space-y-6">
        {/* ... existing header */}
        
        {/* Update the View Resource link/button inside the map: */}
        {step.resource_id && (
            <div className="mt-4 flex items-center gap-2">
              <button 
                onClick={() => handleViewResource(step)}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-500 hover:underline inline-flex items-center gap-1 bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors"
              >
                {step.is_external ? 'Open External Resource' : 'View Materials'} 
                <ExternalLink className="w-3 h-3 ml-1" />
              </button>
            </div>
        )}
      </div>

      <CourseDrawer 
        courseId={selectedCourseId} 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
      />
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/features/plan-stepper.tsx
git commit -m "feat(frontend): integrate CourseDrawer into PlanStepper"
```

---

### Task 4: Final Verification

- [ ] **Step 1: Build the project**

Run: `cd frontend && npm run build`
Expected: Success.

- [ ] **Step 2: Run Seed Script**

Run: `cd backend && .venv/bin/python3 seed.py`
Expected: Courses updated with Markdown content.

- [ ] **Step 3: Commit**

```bash
git commit --allow-empty -m "verify: course materials drawer functional and verified"
```
