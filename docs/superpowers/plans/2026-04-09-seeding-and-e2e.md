# Seed Data & End-to-End Test (Task 9) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seed the database with sample course data and verify the entire system with an end-to-end test.

**Architecture:** 
- **Seeding:** A Python script that inserts course data into PostgreSQL, including pre-computed embeddings (or real ones via OpenAI).
- **E2E Testing:** A script that reads `transcipt.html`, sends it to the backend, and asserts that structured recommendations are returned.

**Tech Stack:** Python, PostgreSQL, HTTPX, OpenAI.

---

### Task 1: Create Seed Data Script

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: Define sample courses**

Include a mix of CS courses (AI, Web, Data Science) with descriptions and skills.

- [ ] **Step 2: Implement insertion logic**

```python
from  db import get_connection
from  embeddings import get_embedding
import json

COURSES = [
    {
        "id": "CS401",
        "subject_name": "Artificial Intelligence",
        "credits": 6.0,
        "description": "Introduction to AI, machine learning, and neural networks.",
        "skills_taught": ["Python", "Machine Learning", "AI"],
        "difficulty": 0.8,
        "workload": 0.7
    },
    # ... more courses
]

def seed():
    with get_connection() as conn:
        with conn.cursor() as cur:
            for c in COURSES:
                emb = get_embedding(c["description"])
                cur.execute(
                    "INSERT INTO courses (id, subject_name, credits, description, skills_taught, difficulty, workload, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                    (c["id"], c["subject_name"], c["credits"], c["description"], json.dumps(c["skills_taught"]), c["difficulty"], c["workload"], emb)
                )
    print("Seeding complete.")
```

---

### Task 2: Implement End-to-End Test

**Files:**
- Create: `tests/test_e2e.py`

- [ ] **Step 1: Write E2E test script**

```python
import unittest
import httpx
import os

class TestEndToEnd(unittest.TestCase):
    def test_full_recommendation_flow(self):
        # 1. Read transcript.html
        with open('transcipt.html', 'r') as f:
            html = f.read()
            
        # 2. Call backend to parse and recommend
        # (Assuming backend is running or mock call)
        pass
```

---
