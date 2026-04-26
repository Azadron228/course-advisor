# Advanced Learning Plan Generator & Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the learning plan system into a multi-plan library with a rich generation form (Generator) collecting skill levels, learning styles, time commitment, and transcript uploads.

**Architecture:**
- **Backend:** Update DB models to store multiple plans and new metadata. Update `AdvisorService` to ingest these parameters into AI generation.
- **Frontend:** Implement a `PlanList` view and a multi-section `LearningPlanGenerator`. Use URL search params (`?id=X` or `?view=new`) for routing within the `/plan` page.

**Tech Stack:** Next.js (Server Components/Actions), FastAPI/SQLAlchemy, Tailwind CSS.

---

### Task 1: Backend Database & Schema Updates

**Files:**
- Modify: `backend/app/infrastructure/db/models.py`
- Modify: `backend/app/api/v1/schemas/auth.py`
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Update ORM models**

```python
# backend/app/infrastructure/db/models.py

class UserORM(Base):
    # ... after existing columns
    default_skill_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    default_learning_style: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    default_study_time: Mapped[Optional[int]] = mapped_column(default=10)

class LearningPlanORM(Base):
    # ... after existing columns
    skill_level: Mapped[str] = mapped_column(String, nullable=False, default="Beginner")
    learning_style: Mapped[str] = mapped_column(String, nullable=False, default="Practical")
    study_time: Mapped[int] = mapped_column(default=10)
    interests: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
```

- [ ] **Step 2: Update Schemas**

```python
# backend/app/api/v1/schemas/auth.py
class UserUpdate(BaseModel):
    # ... existing fields
    default_skill_level: Optional[str] = None
    default_learning_style: Optional[str] = None
    default_study_time: Optional[int] = None

# backend/app/api/v1/schemas/recommendations.py
class LearningPlan(BaseModel):
    id: Optional[int]
    goal: str
    steps: List[LearningPathStep]
    is_active: bool = True
    skill_level: str = "Beginner"
    learning_style: str = "Practical"
    study_time: int = 10
    interests: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/db/models.py backend/app/api/v1/schemas/auth.py backend/app/api/v1/schemas/recommendations.py
git commit -m "feat(backend): update database models and schemas for advanced learning plans"
```

---

### Task 2: Repository & API Updates for Multi-Plan Support

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`
- Modify: `backend/app/api/v1/endpoints/learning_plan.py`

- [ ] **Step 1: Update PlanRepository**

```python
# backend/app/infrastructure/db/repositories/plan_repository.py

from typing import List

class PlanRepository:
    def get_all_plans(self, user_id: int) -> List[LearningPlan]:
        from sqlalchemy import select
        objs = self.db.scalars(
            select(LearningPlanORM).where(LearningPlanORM.user_id == user_id)
        ).all()
        return [
            LearningPlan(
                id=o.id,
                goal=o.goal,
                steps=[LearningPathStep(**step) for step in o.steps],
                is_active=o.is_active,
                skill_level=o.skill_level,
                learning_style=o.learning_style,
                study_time=o.study_time,
                interests=o.interests
            ) for o in objs
        ]

    def get_by_id(self, user_id: int, plan_id: int) -> Optional[LearningPlan]:
        from sqlalchemy import select
        o = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.id == plan_id)
            .where(LearningPlanORM.user_id == user_id)
        )
        if not o: return None
        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[LearningPathStep(**step) for step in o.steps],
            is_active=o.is_active,
            skill_level=o.skill_level,
            learning_style=o.learning_style,
            study_time=o.study_time,
            interests=o.interests
        )
```

- [ ] **Step 2: Update API Endpoints**

```python
# backend/app/api/v1/endpoints/learning_plan.py
from typing import List

@router.get("/", response_model=List[LearningPlan])
async def list_learning_plans(
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    return plan_repo.get_all_plans(current_user.id)

@router.get("/{plan_id}", response_model=LearningPlan)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    plan = plan_repo.get_by_id(current_user.id, plan_id)
    if not plan: raise HTTPException(status_code=404, detail="Plan not found")
    return plan
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py backend/app/api/v1/endpoints/learning_plan.py
git commit -m "feat(backend): add support for listing multiple learning plans"
```

---

### Task 3: Create `PlanList` Component

**Files:**
- Create: `frontend/src/components/features/plan-list.tsx`

- [ ] **Step 1: Implement the list component**

```tsx
'use client';

import { LearningPlan } from '@/components/features/plan-stepper';
import { ChevronRight, Calendar, BookOpen, Clock, Zap } from 'lucide-react';
import { Link } from '@/i18n/routing';

export function PlanList({ plans }: { plans: LearningPlan[] }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-slate-900">My Paths</h1>
        <Link 
          href="/plan?view=new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100"
        >
          <Zap className="w-4 h-4" />
          Create New Plan
        </Link>
      </div>

      <div className="grid gap-4">
        {plans.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl border-2 border-dashed border-slate-200 text-center">
            <BookOpen className="w-16 h-16 text-slate-200 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-slate-900">No paths yet</h3>
            <p className="text-slate-500 mb-6 max-w-xs mx-auto">Start by generating your first personalized learning path.</p>
            <Link 
              href="/plan?view=new"
              className="inline-flex items-center text-indigo-600 font-bold hover:underline"
            >
              Get started <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        ) : (
          plans.map((plan) => (
            <Link 
              key={plan.id}
              href={`/plan?id=${plan.id}`}
              className="group flex items-center justify-between p-6 bg-white rounded-2xl border border-slate-200 hover:border-indigo-300 hover:shadow-xl hover:shadow-indigo-50/50 transition-all"
            >
              <div className="flex-1 min-w-0">
                <h3 className="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors truncate mb-2">
                  {plan.goal}
                </h3>
                <div className="flex flex-wrap gap-4 text-xs font-semibold text-slate-500">
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    {plan.skill_level}
                  </span>
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    <Clock className="w-3 h-3" /> {plan.study_time}h/week
                  </span>
                  <span className="flex items-center gap-1.5 px-2 py-1 bg-slate-100 rounded-md">
                    {plan.steps.length} Steps
                  </span>
                </div>
              </div>
              <div className="ml-6 flex items-center justify-center w-12 h-12 rounded-full bg-slate-50 group-hover:bg-indigo-50 text-slate-400 group-hover:text-indigo-600 transition-all">
                <ChevronRight className="w-6 h-6 group-hover:translate-x-0.5 transition-transform" />
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/features/plan-list.tsx
git commit -m "feat(frontend): add PlanList component"
```

---

### Task 4: Advanced `LearningPlanGenerator` with File Upload

**Files:**
- Create: `frontend/src/components/features/learning-plan-generator.tsx`
- Modify: `frontend/src/app/[locale]/plan/actions.ts`

- [ ] **Step 1: Implement the Generator Form**
(Requires `react-hook-form` and `lucide-react`)

```tsx
'use client';

import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { generatePlanAction } from '@/app/[locale]/plan/actions';
import { Loader2, ArrowRight, Tag, X, Sparkles, Upload, FileText, Check, Clock, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';

const formSchema = z.object({
  goal: z.string().min(5, 'Goal must be at least 5 characters'),
  skill_level: z.enum(['Beginner', 'Intermediate', 'Advanced']),
  learning_style: z.enum(['Visual', 'Practical', 'Theoretical']),
  study_time: z.coerce.number().min(1).max(100),
});

type FormValues = z.infer<typeof formSchema>;

export function LearningPlanGenerator() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { skill_level: 'Beginner', learning_style: 'Practical', study_time: 10 }
  });

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('goal', data.goal);
    formData.append('skill_level', data.skill_level);
    formData.append('learning_style', data.learning_style);
    formData.append('study_time', data.study_time.toString());
    formData.append('interests', JSON.stringify(interests));
    if (file) formData.append('transcript', file);

    try {
      await generatePlanAction(formData);
    } catch (err) {
      console.error(err);
      setIsSubmitting(false);
    }
  };

  // ... (Interest tag logic same as CreatePlanForm)

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
       {/* UI implementation with Goal, Preferences, and Context sections */}
    </div>
  );
}
```

- [ ] **Step 2: Update Server Action**

```typescript
// frontend/src/app/[locale]/plan/actions.ts
export async function generatePlanAction(formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  const file = formData.get('transcript') as File | null;
  if (file && file.size > 0) {
    const parserData = new FormData();
    parserData.append('file', file);
    await fetch(`${API_BASE_URL}/parser/parse-transcript`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: parserData
    });
  }

  const response = await fetch(`${API_BASE_URL}/learning-plan/generate`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json' 
    },
    body: JSON.stringify({
      goal: formData.get('goal'),
      skill_level: formData.get('skill_level'),
      learning_style: formData.get('learning_style'),
      study_time: Number(formData.get('study_time')),
      interests: JSON.parse(formData.get('interests') as string),
    })
  });

  const newPlan = await response.json();
  revalidatePath('/plan');
  redirect(`/plan?id=${newPlan.id}`);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/features/learning-plan-generator.tsx frontend/src/app/[locale]/plan/actions.ts
git commit -m "feat(frontend): implement advanced generator and server action with transcript support"
```

---

### Task 5: Page Orchestration in `PlanPage`

**Files:**
- Modify: `frontend/src/app/[locale]/plan/page.tsx`

- [ ] **Step 1: Update page to handle routing**

```tsx
import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { PlanList } from '@/components/features/plan-list';
import { LearningPlanGenerator } from '@/components/features/learning-plan-generator';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

// getLearningPlans, getLearningPlanById, getUser helpers...

export default async function PlanPage({ searchParams }: { searchParams: Promise<{ id?: string, view?: string }> }) {
  const { id, view } = await searchParams;
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) redirect('/login');

  if (view === 'new') return <LearningPlanGenerator />;

  if (id) {
    const plan = await getLearningPlanById(token, id);
    if (!plan) redirect('/plan');
    return <PlanStepper plan={plan} />;
  }

  const plans = await getLearningPlans(token);
  return <PlanList plans={plans} />;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/plan/page.tsx
git commit -m "feat(plan): implement library view switching and plan deep-linking"
```

---

### Task 6: Final Verification & Build

- [ ] **Step 1: Build the frontend**

Run: `cd frontend && npm run build`
Expected: Success.

- [ ] **Step 2: Verify logic**
Manual check: Navigation between list -> new -> generate -> view works correctly.

- [ ] **Step 3: Commit**

```bash
git commit --allow-empty -m "verify: advanced learning plan library implementation complete"
```
