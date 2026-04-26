# EduPath AI Navigator Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the EduPath AI Navigator frontend prototype using Next.js 14+, mapping the Stitch design system to Tailwind and integrating with the existing FastAPI backend.

**Architecture:** Hybrid App Router approach. Server Components for data fetching (Dashboard, Plan), Client Components for interactivity (Chat, Map). Optimistic UI updates for progress tracking.

**Tech Stack:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, React Query, Zustand, React Hook Form, Zod.

---

### Task 1: Project Scaffold & Design System

**Files:**
- Create: `tailwind.config.ts` (with design tokens)
- Create: `src/app/globals.css`
- Create: `src/lib/utils.ts` (cn helper)

- [ ] **Step 1: Initialize Tailwind with Stitch Tokens**
Map primary indigo (#4F46E5), secondary green (#10B981), and Lexend/Inter fonts to the config.

- [ ] **Step 2: Setup Base Layout & Global Styles**
Implement the "Level 0" background (#f8f9ff) and card styles.

---

### Task 2: API Client & Authentication

**Files:**
- Create: `src/lib/api-client.ts`
- Create: `src/hooks/use-auth.ts`
- Create: `src/middleware.ts`

- [ ] **Step 1: Create typed API Wrapper**
Implement a fetch wrapper that handles JWT headers and global error toast notifications.

- [ ] **Step 2: Implement Auth Middleware**
Protect all routes except `/login`. Redirect unauthenticated users.

---

### Task 3: Global Navigation & Layout

**Files:**
- Create: `src/app/layout.tsx`
- Create: `src/components/shared/sidebar.tsx`
- Create: `src/components/shared/top-nav.tsx`

- [ ] **Step 1: Implement Persistent Sidebar**
Use the "Soft Geometricism" (8px radius) and Indigo active states.

- [ ] **Step 2: Setup Navigation Context**
Use Zustand to manage sidebar collapse state and mobile drawer.

---

### Task 4: Unified Dashboard (Navigation Hub)

**Files:**
- Create: `src/app/dashboard/page.tsx` (Server Component)
- Create: `src/components/features/dashboard-summary.tsx`

- [ ] **Step 1: Fetch Dashboard Data**
Call `GET /api/v1/dashboard/` in a Server Component.

- [ ] **Step 2: Build Navigation Hub Cards**
Implement cards for "Continue Learning" (Active Plan) and "Advisor Suggestions" with the soft shadow model (Level 1).

---

### Task 5: Learning Plan Timeline

**Files:**
- Create: `src/app/plan/page.tsx` (Server Component)
- Create: `src/components/features/plan-stepper.tsx`
- Create: `src/app/plan/actions.ts` (Server Action)

- [ ] **Step 1: Fetch Active Plan**
Call `GET /api/v1/learning-plan/`.

- [ ] **Step 2: Implement Step Completion**
Build the stepper UI with positive reinforcement (Green secondary color). Use Server Actions to `PATCH /learning-plan/steps/{id}`.

---

### Task 6: AI Advisor Chat

**Files:**
- Create: `src/app/chat/page.tsx` (Client Component)
- Create: `src/components/features/chat-window.tsx`
- Create: `src/hooks/use-chat.ts`

- [ ] **Step 1: Implement Chat State with React Query**
Handle message history and the `POST /recommendations/chat` mutation.

- [ ] **Step 2: Polish Chat UI**
Add "thinking" indicators and gradient borders for dynamically generated content.

---

### Task 7: Interactive Skill Map (SVG)

**Files:**
- Create: `src/app/map/page.tsx`
- Create: `src/components/features/skill-graph.tsx`

- [ ] **Step 1: Render Nodes from Backend**
Fetch `GET /api/v1/skills/map/` and render as SVG nodes.

- [ ] **Step 2: Derive Edges**
Implement logic to draw lines between nodes based on their sequencing in the current learning plan.

---

### Task 8: Profile & Onboarding Wizard

**Files:**
- Create: `src/app/profile/page.tsx`
- Create: `src/components/features/onboarding-wizard.tsx`

- [ ] **Step 1: Implement Profile Edit**
Use React Hook Form + Zod for `PATCH /api/v1/users/me`.

- [ ] **Step 2: Build Onboarding Flow**
Create a multi-step client wizard for new users (where `onboarding_completed` is false).
