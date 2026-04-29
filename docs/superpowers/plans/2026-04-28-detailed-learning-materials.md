# Detailed Learning Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure every step in the learning path has detailed materials (internal or external) and display them in the UI.

**Architecture:** Update the learning path data structure to include a list of detailed materials for each step. Enhance the AI prompt to generate these materials. Update the frontend to display the materials.

**Tech Stack:** FastAPI (Python), SQLAlchemy, Pydantic, LlamaIndex, React (Next.js), Tailwind CSS.

---

### Task 1: Update Backend Domain Entities

**Files:**
- Modify: `backend/app/domain/recommendation/entities.py`

- [ ] **Step 1: Add LearningMaterial dataclass and update LearningPathStep**

```python
@dataclass(frozen=True)
class LearningMaterial:
    title: str
    description: str
    url: Optional[str] = None
    type: str = "article"  # e.g., video, article, course, documentation

@dataclass(frozen=True)
class LearningPathStep:
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    status: str = "upcoming"
    materials: List[LearningMaterial] = field(default_factory=list)
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/domain/recommendation/entities.py
git commit -m "domain: add LearningMaterial and update LearningPathStep"
```

### Task 2: Update API Schemas

**Files:**
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Add LearningMaterial Pydantic model and update LearningPathStep**

```python
class LearningMaterial(BaseModel):
    title: str
    description: str
    url: Optional[str] = None
    type: str = "article"
    model_config = ConfigDict(from_attributes=True)

class LearningPathStep(BaseModel):
    order: int
    title: str
    description: str
    resource_id: Optional[str] = None
    is_external: bool = False
    status: str = "upcoming"
    materials: List[LearningMaterial] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/api/v1/schemas/recommendations.py
git commit -m "api: update schemas for detailed materials"
```

### Task 3: Update AI Analysis Agent

**Files:**
- Modify: `backend/app/infrastructure/ai/analysis_agent.py`

- [ ] **Step 1: Update prompt to require detailed materials**

Update the `prompt_template_str` to explicitly demand detailed materials for every step.

```python
    prompt_template_str = (
        "You are a senior academic strategist. Your goal is to provide a comprehensive "
        "skill gap analysis and a structured learning path for a student based on their "
        "transcript and a list of available courses.\n\n"
        "1. Skill Gap Map: Identify missing skills and group them by domain.\n"
        "2. Domain Scores: Provide a 0-1 gap score per domain.\n"
        "3. Learning Path: Suggest a logical sequence of courses (internal or external) to fill these gaps.\n"
        "   - EVERY step MUST include at least 1-2 detailed materials.\n"
        "   - Materials MUST have a 'title', a 'description' (at least 2-3 sentences of detailed content/what to learn), and a 'url' if external.\n"
        "   - If the step uses an internal course, include it as a material with its details.\n"
        "   - If external, provide high-quality links (Coursera, edX, YouTube, Documentation).\n\n"
        "Always prioritize filling critical prerequisites and foundational skills first.\n\n"
        f"Student Transcript: {transcript_summary}\n"
        f"Student Current Skills: {current_skills}\n\n"
        f"Available Internal Courses:\n{available_courses}\n\n"
        f"User Goal and Context: {goal_msg}\n\n"
        "Output ONLY valid JSON matching the schema."
    )
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/infrastructure/ai/analysis_agent.py
git commit -m "ai: enhance prompt for detailed materials generation"
```

### Task 4: Update Plan Repository Mapping

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Ensure materials are correctly mapped in from_orm/to_orm logic**

```python
    def _to_domain(self, o: LearningPlanORM) -> LearningPlan:
        return LearningPlan(
            id=o.id,
            goal=o.goal,
            steps=[
                LearningPathStep(
                    **{k: v for k, v in step.items() if k != "materials"},
                    materials=[LearningMaterial(**m) for m in step.get("materials", [])]
                ) 
                for step in o.steps
            ],
            is_active=o.is_active,
            skill_level=o.skill_level,
            learning_style=o.learning_style,
            study_time=o.study_time,
            interests=o.interests,
        )
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "infra: update repository mapping for materials"
```

### Task 5: Update Frontend Types and UI

**Files:**
- Modify: `frontend/src/components/features/plan-stepper.tsx`

- [ ] **Step 1: Update interface and UI to display materials**

Add `LearningMaterial` interface and update `LearningPathStep`.
Render a list of materials in each step.

```typescript
export interface LearningMaterial {
  title: string;
  description: string;
  url?: string;
  type: string;
}

export interface LearningPathStep {
  // ... existing fields
  materials: LearningMaterial[];
}

// In PlanStepper render loop:
{step.materials && step.materials.length > 0 && (
  <div className="mt-4 space-y-3">
    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">{t('materials')}</h4>
    {step.materials.map((mat, midx) => (
      <div key={midx} className="p-3 bg-slate-50 rounded-lg border border-slate-100">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-bold text-slate-800">{mat.title}</span>
          {mat.url && (
            <a href={mat.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500">
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">{mat.description}</p>
      </div>
    ))}
  </div>
)}
```

- [ ] **Step 2: Commit changes**

```bash
git add frontend/src/components/features/plan-stepper.tsx
git commit -m "frontend: display detailed materials in plan stepper"
```

### Task 6: Verification

- [ ] **Step 1: Generate a new learning plan**
- [ ] **Step 2: Verify that steps have materials in the DB/API response**
- [ ] **Step 3: Verify that materials are displayed with detailed descriptions in the UI**
