# Prototype UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely overhaul the application to match the new "EduPath AI Navigator" prototype design system, creating new pages and supporting backend endpoints.

**Architecture:** We will implement the "Guided Clarity" design system using Tailwind CSS variables in the frontend. We will create dedicated feature pages (`/dashboard/skills`, `/dashboard/profile`, `/dashboard/chat`) rather than a single monolithic dashboard, and add corresponding REST endpoints to the FastAPI backend.

**Tech Stack:** Next.js (App Router), Tailwind CSS, Framer Motion, FastAPI, Python.

---

### Task 1: Establish the Design System Core

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/tailwind.config.ts` (or equivalent if inline)
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Inject Design Tokens into CSS**
Update `frontend/src/app/globals.css` to include the prototype's color palette.

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lexend:wght@500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: #f8f9ff;
    --surface: #ffffff;
    --surface-dim: #cbdbf5;
    --primary: #4F46E5;
    --primary-hover: #3b34b9;
    --secondary: #10B981;
    --text-main: #0b1c30;
    --text-muted: #464555;
    --border-light: #F1F5F9;
  }
  body {
    background-color: var(--background);
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
  }
  h1, h2, h3, h4, h5, h6 {
    font-family: 'Lexend', sans-serif;
  }
}
```

- [ ] **Step 2: Update Layout Fonts**
Modify `frontend/src/app/layout.tsx` to ensure proper body styling.

```tsx
import './globals.css';
import React from 'react';
import { AuthProvider } from '@/lib/auth-context';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[var(--background)] text-[var(--text-main)] font-sans antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Commit Design System**
```bash
git add frontend/src/app/globals.css frontend/src/app/layout.tsx
git commit -m "style: apply Guided Clarity design system tokens"
```

---

### Task 2: Implement UI Primitives

**Files:**
- Create: `frontend/src/components/ui/Card.tsx`
- Create: `frontend/src/components/ui/Button.tsx`

- [ ] **Step 1: Create standard Card component**
Create `frontend/src/components/ui/Card.tsx` implementing Level 1 elevation and 16px radius.

```tsx
import React from 'react';

export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-2xl border border-[var(--border-light)] shadow-[0px_4px_20px_rgba(0,0,0,0.04)] p-6 ${className}`}>
      {children}
    </div>
  );
}
```

- [ ] **Step 2: Create standard Button component**
Create `frontend/src/components/ui/Button.tsx` with 8px radius and primary/secondary variants.

```tsx
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
}

export function Button({ children, variant = 'primary', className = '', ...props }: ButtonProps) {
  const baseStyle = "px-4 py-2 rounded-lg font-medium transition-colors duration-200";
  const variants = {
    primary: "bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]",
    secondary: "bg-[var(--secondary)] text-white hover:bg-emerald-600",
    outline: "border-2 border-[var(--border-light)] text-[var(--text-muted)] hover:border-[var(--primary)]"
  };

  return (
    <button className={`${baseStyle} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
```

- [ ] **Step 3: Commit Components**
```bash
git add frontend/src/components/ui/
git commit -m "feat: add Card and Button primitives"
```

---

### Task 3: Backend API for Interactive Skill Map

**Files:**
- Modify: `backend/app/api/v1/router.py`
- Create: `backend/app/api/v1/endpoints/skills.py`
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Define Skill Schema**
Append to `backend/app/api/v1/schemas/recommendations.py`.

```python
from pydantic import BaseModel
from typing import List

class SkillNode(BaseModel):
    id: str
    label: str
    mastery_level: int # 0 to 100
    category: str

class SkillMapResponse(BaseModel):
    nodes: List[SkillNode]
```

- [ ] **Step 2: Create Skills Endpoint**
Create `backend/app/api/v1/endpoints/skills.py`.

```python
from fastapi import APIRouter, Depends
from typing import List
from app.api.deps import get_current_active_user
from app.api.v1.schemas.auth import UserPublic as User
from app.api.v1.schemas.recommendations import SkillMapResponse, SkillNode

router = APIRouter()

@router.get("/map", response_model=SkillMapResponse)
async def get_skill_map(current_user: User = Depends(get_current_active_user)):
    # Mock data for the prototype skill map
    nodes = [
        SkillNode(id="ml1", label="Machine Learning Basics", mastery_level=80, category="AI"),
        SkillNode(id="web1", label="Frontend Development", mastery_level=40, category="Engineering"),
        SkillNode(id="data1", label="Data Structures", mastery_level=90, category="Computer Science")
    ]
    return SkillMapResponse(nodes=nodes)
```

- [ ] **Step 3: Register Router**
Edit `backend/app/api/v1/router.py` to include the new endpoint.

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, recommendations, users, admin, parser, skills

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(parser.router, prefix="/parser", tags=["parser"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"]) # Added
```

- [ ] **Step 4: Commit Backend API**
```bash
git add backend/app/api/v1/
git commit -m "feat: add skill map API endpoint"
```

---

### Task 4: Interactive Skill Map Page

**Files:**
- Create: `frontend/src/app/dashboard/skills/page.tsx`

- [ ] **Step 1: Implement the UI**
Create the page to fetch and render the skill map.

```tsx
'use client';
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface SkillNode {
  id: string;
  label: string;
  mastery_level: number;
  category: string;
}

export default function SkillMapPage() {
  const [skills, setSkills] = useState<SkillNode[]>([]);

  useEffect(() => {
    api.get('/api/v1/skills/map').then(res => setSkills(res.data.nodes)).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-[1280px] mx-auto">
      <h1 className="text-4xl font-bold mb-8">Interactive Skill Map</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {skills.map(skill => (
          <Card key={skill.id} className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-semibold tracking-wider uppercase text-[var(--text-muted)]">{skill.category}</span>
              <span className="text-sm font-medium text-[var(--primary)]">{skill.mastery_level}%</span>
            </div>
            <h3 className="text-xl font-semibold">{skill.label}</h3>
            <div className="h-2 w-full bg-[var(--border-light)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[var(--secondary)] rounded-full transition-all" 
                style={{ width: `${skill.mastery_level}%` }}
              />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit Frontend Page**
```bash
git add frontend/src/app/dashboard/skills/
git commit -m "feat: implement Interactive Skill Map UI"
```

---

### Task 5: Backend API for Profile & Learning Plan

**Files:**
- Create: `backend/app/api/v1/endpoints/learning_plan.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] **Step 1: Create Endpoint**
Create `backend/app/api/v1/endpoints/learning_plan.py`.

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api.deps import get_current_active_user
from app.api.v1.schemas.auth import UserPublic as User

router = APIRouter()

class PlanStep(BaseModel):
    title: str
    description: str
    status: str # 'completed', 'current', 'upcoming'

class LearningPlanResponse(BaseModel):
    career_goal: str
    steps: List[PlanStep]

@router.get("/", response_model=LearningPlanResponse)
async def get_learning_plan(current_user: User = Depends(get_current_active_user)):
    steps = [
        PlanStep(title="Intro to Python", description="Master basic syntax", status="completed"),
        PlanStep(title="Data Structures", description="Learn lists, dicts, sets", status="current"),
        PlanStep(title="Machine Learning", description="Build first model", status="upcoming"),
    ]
    return LearningPlanResponse(career_goal="AI Engineer", steps=steps)
```

- [ ] **Step 2: Register Router**
Edit `backend/app/api/v1/router.py`.

```python
from app.api.v1.endpoints import learning_plan
# ... add inside the file ...
api_router.include_router(learning_plan.router, prefix="/learning-plan", tags=["learning-plan"])
```

- [ ] **Step 3: Commit Backend**
```bash
git add backend/app/api/v1/
git commit -m "feat: add learning plan endpoint"
```

---

### Task 6: Profile & Learning Plan Page

**Files:**
- Create: `frontend/src/app/dashboard/profile/page.tsx`

- [ ] **Step 1: Implement UI**
```tsx
'use client';
import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface PlanStep {
  title: string;
  description: string;
  status: string;
}

export default function ProfilePlanPage() {
  const [goal, setGoal] = useState('');
  const [steps, setSteps] = useState<PlanStep[]>([]);

  useEffect(() => {
    api.get('/api/v1/learning-plan').then(res => {
      setGoal(res.data.career_goal);
      setSteps(res.data.steps);
    });
  }, []);

  return (
    <div className="p-8 max-w-[1280px] mx-auto">
      <h1 className="text-4xl font-bold mb-2">Learning Plan</h1>
      <p className="text-[var(--text-muted)] mb-8 text-lg">Goal: {goal}</p>
      
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <Card key={idx} className={step.status === 'current' ? 'border-[var(--primary)] shadow-md' : ''}>
            <div className="flex items-start gap-4">
              <div className={`w-3 h-3 mt-2 rounded-full ${step.status === 'completed' ? 'bg-[var(--secondary)]' : step.status === 'current' ? 'bg-[var(--primary)]' : 'bg-gray-300'}`} />
              <div>
                <h3 className="text-xl font-semibold">{step.title}</h3>
                <p className="text-[var(--text-muted)]">{step.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit Profile Page**
```bash
git add frontend/src/app/dashboard/profile/
git commit -m "feat: implement Profile and Learning Plan UI"
```

---

### Task 7: AI Advisor Chat Modal / Page Refactor

**Files:**
- Create: `frontend/src/app/dashboard/chat/page.tsx`

- [ ] **Step 1: Refactor Chat into its own view**
Extract chat from the sidebar and give it the spacious "Guided Clarity" treatment.

```tsx
'use client';
import React, { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface Msg {
  role: string;
  content: string;
}

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [msgs, setMsgs] = useState<Msg[]>([]);

  useEffect(() => {
    api.get('/api/v1/recommendations/chat/history').then(res => setMsgs(res.data)).catch(console.error);
  }, []);

  const send = async () => {
    if (!input) return;
    const userMsg = { role: 'user', content: input };
    setMsgs([...msgs, userMsg]);
    setInput('');
    try {
      const res = await api.post('/api/v1/recommendations/chat', { message: userMsg.content });
      setMsgs(res.data.history);
    } catch (e) {}
  };

  return (
    <div className="p-8 max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      <h1 className="text-4xl font-bold mb-8">AI Advisor</h1>
      
      <Card className="flex-1 overflow-y-auto mb-4 flex flex-col gap-4 p-8 bg-gradient-to-b from-white to-[#fcfcff]">
        {msgs.map((m, i) => (
          <div key={i} className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-[var(--primary)] text-white self-end rounded-tr-sm' : 'bg-[var(--border-light)] text-[var(--text-main)] self-start rounded-tl-sm'}`}>
            {m.content}
          </div>
        ))}
      </Card>

      <div className="flex gap-4">
        <input 
          className="flex-1 rounded-lg border border-[var(--border-light)] p-4 focus:outline-none focus:border-[var(--primary)] bg-[var(--border-light)] focus:bg-white transition-colors"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your learning journey..."
          onKeyDown={e => e.key === 'Enter' && send()}
        />
        <Button onClick={send} className="px-8 text-lg">Send</Button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit Chat UI**
```bash
git add frontend/src/app/dashboard/chat/
git commit -m "feat: implement standalone AI Advisor Chat page"
```
