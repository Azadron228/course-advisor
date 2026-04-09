# Alembic Transition & Task 3 (Models & Parser) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition to Alembic migrations for database schema management and implement Pydantic models with a BeautifulSoup transcript parser.

**Architecture:** 
- **Database:** Alembic for migrations, managing `vector` extension and `courses` table.
- **Backend:** Pydantic v2 for data models, BeautifulSoup4 for HTML transcript parsing.

**Tech Stack:** Alembic, SQLAlchemy (for Alembic), Pydantic, BeautifulSoup4.

---

### Task 1: Setup Alembic Migrations

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/initial_migration.py`

- [ ] **Step 1: Update backend/requirements.txt**

```text
fastapi
uvicorn
pydantic-ai
psycopg[binary]
pgvector
beautifulsoup4
openai
alembic
sqlalchemy
```

- [ ] **Step 2: Initialize Alembic**

Run: `cd backend && alembic init alembic`

- [ ] **Step 3: Configure alembic.ini**

Update `sqlalchemy.url` to use an environment variable or a placeholder that we'll override in `env.py`.

- [ ] **Step 4: Update alembic/env.py to use DATABASE_URL**

Modify `alembic/env.py` to pull the connection string from the `DATABASE_URL` environment variable.

- [ ] **Step 5: Create Initial Migration for Courses Table**

```python
"""initial migration

Revision ID: <auto-gen>
Revises: 
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        'courses',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('subject_name', sa.String(), nullable=False),
        sa.Column('credits', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('skills_taught', sa.JSON(), nullable=False),
        sa.Column('difficulty', sa.Float(), sa.CheckConstraint('difficulty >= 0 AND difficulty <= 1')),
        sa.Column('workload', sa.Float(), sa.CheckConstraint('workload >= 0 AND workload <= 1')),
        sa.Column('embedding', Vector(1536))
    )

def downgrade():
    op.drop_table('courses')
    op.execute("DROP EXTENSION IF EXISTS vector")
```

- [ ] **Step 6: Run Migration**

Run: `cd backend && alembic upgrade head`

- [ ] **Step 7: Update backend/db.py to remove init_db**

Remove the `init_db` function and just keep `get_connection`.

- [ ] **Step 8: Verify with tests/test_db.py**

Run: `pytest tests/test_db.py`

---

### Task 2: Implement Pydantic Models (Task 3.1)

**Files:**
- Create: `backend/models.py`

- [ ] **Step 1: Write failing test for models**

```python
import unittest
from backend.models import TranscriptEntry, Student, Course

class TestModels(unittest.TestCase):
    def test_transcript_entry_validation(self):
        entry = TranscriptEntry(subject_name="Math", credits=6.0, mark=85.0)
        self.assertEqual(entry.subject_name, "Math")
        
        with self.assertRaises(ValueError):
            TranscriptEntry(subject_name="Invalid", credits=6.0, mark=105.0)
```

- [ ] **Step 2: Implement models**

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class TranscriptEntry(BaseModel):
    subject_name: str
    credits: float
    mark: float = Field(ge=0, le=100)

class Student(BaseModel):
    id: str
    name: str
    transcript: List[TranscriptEntry]
    current_skills: List[str]

class Course(BaseModel):
    id: str
    subject_name: str
    credits: float
    description: str
    prerequisites: List[str]
    skills_taught: List[str]
    difficulty: float = Field(ge=0, le=1)
    workload: float = Field(ge=0, le=1)
```

- [ ] **Step 3: Run tests**

---

### Task 3: Implement Transcript Parser (Task 3.2)

**Files:**
- Create: `backend/parser.py`

- [ ] **Step 1: Write failing test for parser**

```python
import unittest
from backend.parser import parse_transcript_html

class TestParser(unittest.TestCase):
    def test_parse_transcript(self):
        html = """
        <table>
            <tr><td>Subject</td><td>Credits</td><td>Mark</td></tr>
            <tr><td>Algorithms</td><td>6.0</td><td>80.0</td></tr>
        </table>
        """
        entries = parse_transcript_html(html)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].subject_name, "Algorithms")
```

- [ ] **Step 2: Implement parser using BeautifulSoup**

- [ ] **Step 3: Run tests**

---
