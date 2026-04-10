# Agent & Orchestration (Tasks 6 & 7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the PydanticAI Agent for RAG-based reasoning and the Hybrid Scorer Orchestrator.

**Architecture:** 
- **RAG Scorer (Agent):** Uses PydanticAI to analyze course content against student goals/transcript and provide a score + reasoning.
- **Hybrid Scorer:** Combines Content, Skill Gap, RAG, and Preference scores using weighted averages.

**Tech Stack:** Python, PydanticAI, FastAPI (context), Pydantic.

---

### Task 1: Implement PydanticAI Agent (Task 6)

**Files:**
- Create: `backend/agent.py`

- [ ] **Step 1: Define Agent and Output Schema**

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class AgentRecommendation(BaseModel):
    score: float # 0 to 1
    reasoning: str
    tags: list[str]

# Define agent with system prompt
recommendation_agent = Agent(
    'openai:gpt-4o', # or local model
    result_type=AgentRecommendation,
    system_prompt="You are a university advisor..."
)
```

- [ ] **Step 2: Implement RAG Scorer**

```python
from  agent import recommendation_agent

class RAGScorer:
    async def score(self, student: Student, course: Course) -> AgentRecommendation:
        # Prompt agent with student transcript and course description
        pass
```

---

### Task 2: Implement Hybrid Scorer Orchestration (Task 7)

**Files:**
- Create: `backend/scoring/orchestrator.py`
- Modify: `backend/models.py` (Add RecommendationResult models if not present)

- [ ] **Step 1: Implement Recommendation Models in models.py**

(Referring to the design spec for `RecommendationResult` and `RecommendationResponse`)

- [ ] **Step 2: Implement HybridScorer Orchestrator**

```python
class HybridScorer:
    def __init__(self):
        self.content_scorer = ContentScorer()
        self.skill_gap_scorer = SkillGapScorer()
        self.rag_scorer = RAGScorer()
        # Add PreferenceScorer later or now
        
    async def recommend(self, student: Student, courses: list[Course]) -> RecommendationResponse:
        # 1. Loop through courses
        # 2. Get scores from all components
        # 3. Apply weights: 30% Content, 30% Skill Gap, 20% RAG, 20% Preference
        # 4. Return sorted RecommendationResponse
        pass
```

- [ ] **Step 3: Write tests for Orchestrator**

---
