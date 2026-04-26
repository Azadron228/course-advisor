# Learning Plan Creation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate onboarding and learning plan generation into a single, unified flow on the `/plan` page.

**Architecture:** Remove the global `OnboardingWizard` modal and move its logic into a new `CreatePlanForm` that renders on `/plan` if no active plan exists. Use a server action to handle the multi-step process (profile update + generation).

**Tech Stack:** Next.js (Server Actions), React Hook Form, Zod, Tailwind CSS.

---

### Task 1: Add `generatePlanAction` to Server Actions

**Files:**
- Modify: `frontend/src/app/[locale]/plan/actions.ts`

- [ ] **Step 1: Implement the server action**

```typescript
import { revalidatePath } from 'next/cache';
import { cookies } from 'next/headers';
import { API_BASE_URL } from '@/lib/config';

export async function generatePlanAction(data: {
  full_name: string;
  career_goal: string;
  interests: string[];
}) {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    throw new Error('Authentication required');
  }

  // 1. Update user profile
  const profileResponse = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      full_name: data.full_name,
      career_goal: data.career_goal,
      onboarding_completed: true,
    }),
  });

  if (!profileResponse.ok) {
    throw new Error('Failed to update profile');
  }

  // 2. Generate learning plan
  const planResponse = await fetch(`${API_BASE_URL}/learning-plan/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!planResponse.ok) {
    throw new Error('Failed to generate learning plan');
  }

  revalidatePath('/plan');
  revalidatePath('/dashboard');
  return { success: true };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/plan/actions.ts
git commit -m "feat(plan): add generatePlanAction server action"
```

---

### Task 2: Create `CreatePlanForm` Component

**Files:**
- Create: `frontend/src/components/features/create-plan-form.tsx`

- [ ] **Step 1: Implement the form component**

```tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { generatePlanAction } from '@/app/[locale]/plan/actions';
import { Loader2, ArrowRight, Tag, X, Sparkles } from 'lucide-react';

const formSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  career_goal: z.string().min(5, 'Career goal must be at least 5 characters'),
});

type FormValues = z.infer<typeof formSchema>;

export function CreatePlanForm({ initialName = '' }: { initialName?: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interests, setInterests] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      full_name: initialName,
      career_goal: '',
    },
  });

  const handleAddInterest = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault();
      if (!interests.includes(currentTag.trim())) {
        setInterests([...interests, currentTag.trim()]);
      }
      setCurrentTag('');
    }
  };

  const removeInterest = (tag: string) => {
    setInterests(interests.filter((t) => t !== tag));
  };

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    setError(null);
    try {
      await generatePlanAction({
        ...data,
        interests,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate plan');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Start Your Learning Journey</h1>
        <p className="text-slate-500 text-lg">Tell us your goals, and our AI will draft a personalized path for you.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xl space-y-6">
        {error && (
          <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Full Name</label>
            <input
              {...register('full_name')}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
              placeholder="e.g. Alex Johnson"
            />
            {errors.full_name && <p className="text-xs text-red-500">{errors.full_name.message}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">What is your career goal?</label>
            <textarea
              {...register('career_goal')}
              rows={3}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
              placeholder="e.g. I want to become a Senior Frontend Engineer focusing on React and AI."
            />
            {errors.career_goal && <p className="text-xs text-red-500">{errors.career_goal.message}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Interests & Topics</label>
            <div className="relative">
              <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                onKeyDown={handleAddInterest}
                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all text-slate-900"
                placeholder="Type and press Enter (e.g. TypeScript, UI Design)"
              />
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {interests.map((tag) => (
                <span key={tag} className="flex items-center gap-1 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold border border-indigo-100">
                  {tag}
                  <button type="button" onClick={() => removeInterest(tag)} className="hover:text-indigo-900">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-indigo-200 disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Drafting Your Plan...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate My Learning Path
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/features/create-plan-form.tsx
git commit -m "feat(plan): add CreatePlanForm component"
```

---

### Task 3: Update `PlanPage` to Render `CreatePlanForm`

**Files:**
- Modify: `frontend/src/app/[locale]/plan/page.tsx`

- [ ] **Step 1: Update the page logic**

```tsx
import { cookies } from 'next/headers';
import { PlanStepper, LearningPlan } from '@/components/features/plan-stepper';
import { CreatePlanForm } from '@/components/features/create-plan-form';
import { redirect } from 'next/navigation';
import { API_BASE_URL } from '@/lib/config';

async function getLearningPlan(): Promise<LearningPlan | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) {
    redirect('/login');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/learning-plan/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Cache-Control': 'no-cache',
      },
    });

    if (response.status === 401) {
      redirect('/login');
    }

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error('Failed to fetch learning plan');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching learning plan:', error);
    return null;
  }
}

async function getUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  if (!token) return null;

  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) return null;
  return response.json();
}

export default async function PlanPage() {
  const [plan, user] = await Promise.all([getLearningPlan(), getUser()]);

  return (
    <div className="py-4">
      {plan ? (
        <PlanStepper plan={plan} />
      ) : (
        <CreatePlanForm initialName={user?.full_name} />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/plan/page.tsx
git commit -m "feat(plan): conditionally render CreatePlanForm on plan page"
```

---

### Task 4: Remove `OnboardingWizard` Integration

**Files:**
- Modify: `frontend/src/components/shared/main-layout.tsx`
- Delete: `frontend/src/components/features/onboarding-wizard.tsx`

- [ ] **Step 1: Remove from `MainLayout.tsx`**

```tsx
'use client';

import { usePathname } from 'next/navigation';
import { Sidebar } from './sidebar';
import { TopNav } from './top-nav';
import { MobileDrawer } from './mobile-drawer';
import { useAuth } from '@/hooks/use-auth';

const PUBLIC_ROUTES = ['/login', '/register', '/'];

export function MainLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading } = useAuth();

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);

  if (isPublicRoute) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
      <MobileDrawer />
    </div>
  );
}
```

- [ ] **Step 2: Delete the onboarding file**

Run: `rm frontend/src/components/features/onboarding-wizard.tsx`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/shared/main-layout.tsx
git rm frontend/src/components/features/onboarding-wizard.tsx
git commit -m "cleanup: remove global OnboardingWizard"
```

---

### Task 5: Remove Onboarding Nudge from Dashboard

**Files:**
- Modify: `frontend/src/app/[locale]/dashboard/page.tsx`

- [ ] **Step 1: Remove the banner**

```tsx
import React from 'react';
import { cookies } from 'next/headers';
import Link from 'next/link';
import { 
  ClipboardList, 
  Map, 
  MessageSquare, 
  ArrowRight,
  TrendingUp,
  Award,
  Zap
} from 'lucide-react';
import { DashboardSummary } from '@/components/features/dashboard-summary';
import { API_BASE_URL } from '@/lib/config';

// ... (interface and getDashboardData remains same)

export default async function DashboardPage() {
  const data = await getDashboardData();

  const navCards = [
    // ... (same as before)
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <DashboardSummary 
        welcomeMessage={data.welcome_message}
        activePlanTitle={data.active_plan_title}
        progressPercentage={data.progress_percentage}
      />

      <div className="space-y-4">
        {/* ... Navigation Hub section same as before */}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* ... Bottom grid same as before */}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/[locale]/dashboard/page.tsx
git commit -m "cleanup: remove onboarding nudge from dashboard"
```

---

### Task 6: Final Verification

- [ ] **Step 1: Build the frontend**

Run: `cd frontend && npm run build`
Expected: Successful build without type errors.

- [ ] **Step 2: Verify logic**
Manual check: New users should see the plan creation form on `/plan`. Existing users with a plan should see the stepper. Onboarding modal should never appear.

- [ ] **Step 3: Commit**

```bash
git commit --allow-empty -m "verify: implementation complete and verified"
```
