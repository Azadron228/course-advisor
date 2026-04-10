# Scoring Components (Tasks 4 & 5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Content Scorer (pgvector similarity) and Skill Gap Scorer (set difference).

**Architecture:** 
- **Content Scorer:** Queries `pgvector` in PostgreSQL to find courses with descriptions similar to the student's transcript subjects.
- **Skill Gap Scorer:** Compares the skills taught in a course against the student's current skills to identify gaps.

**Tech Stack:** Python, PostgreSQL, pgvector, Pydantic, OpenAI (for embeddings).

---

### Task 1: Implement Content Scorer (Task 4)

**Files:**
- Create: `backend/scoring/content.py`
- Create: `backend/embeddings.py`

- [ ] **Step 1: Write embedding utility**

Implement `get_embedding` in `backend/embeddings.py` using the `openai` client. (Assuming an API key will be provided via environment).

- [ ] **Step 2: Write failing test for Content Scorer**

```python
import unittest
from  scoring.content import ContentScorer
from  models import Student, TranscriptEntry

class TestContentScorer(unittest.TestCase):
    def test_score_calculation(self):
        scorer = ContentScorer()
        student = Student(
            id="S1", name="Test", 
            transcript=[TranscriptEntry(subject_name="Python", credits=6, mark=80)],
            current_skills=[]
        )
        # Mock database and embedding responses in implementation or use a real test DB
        pass
```

- [ ] **Step 3: Implement Content Scorer**

```python
from  db import get_connection
from  embeddings import get_embedding

class ContentScorer:
    def score(self, student: Student, course_id: str) -> float:
        # 1. Aggregate transcript subject names
        # 2. Get embedding for the aggregated text
        # 3. Query pgvector for cosine similarity to course.embedding
        pass
```

- [ ] **Step 4: Run tests**

---

### Task 2: Implement Skill Gap Scorer (Task 5)

**Files:**
- Create: `backend/scoring/skill_gap.py`

- [ ] **Step 1: Write failing test for Skill Gap Scorer**

```python
import unittest
from  scoring.skill_gap import SkillGapScorer
from  models import Student, Course

class TestSkillGapScorer(unittest.TestCase):
    def test_skill_gap_score(self):
        student = Student(id="S1", name="A", transcript=[], current_skills=["Python"])
        course = Course(
            id="C1", subject_name="Adv Python", credits=6, 
            description="...", prerequisites=[], 
            skills_taught=["Python", "Django", "FastAPI"],
            difficulty=0.5, workload=0.5
        )
        scorer = SkillGapScorer()
        score = scorer.score(student, course)
        # 2 out of 3 skills are new. Score should represent the "gap" or "coverage".
        # If score is 1.0 - (common / taught), it would be 1.0 - (1/3) = 0.66
        self.assertAlmostEqual(score, 0.66, places=2)
```

- [ ] **Step 2: Implement Skill Gap Scorer**

```python
class SkillGapScorer:
    def score(self, student: Student, course: Course) -> float:
        taught = set(course.skills_taught)
        current = set(student.current_skills)
        if not taught: return 0.0
        new_skills = taught - current
        return len(new_skills) / len(taught)
```

- [ ] **Step 3: Run tests**

---
