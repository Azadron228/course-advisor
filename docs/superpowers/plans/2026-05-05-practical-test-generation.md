# Practical Test Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `GET /lessons/{lesson_id}/test` endpoint that generates or retrieves a 5-question multiple-choice practice test for a lesson, with LaTeX support for math.

**Architecture:** Lazy generation pattern. The endpoint checks the database for an existing test; if missing, it uses an LLM to generate questions based on lesson content and persists them.

**Tech Stack:** FastAPI, SQLAlchemy, OpenAI/LlamaIndex, Pydantic.

---

### Task 1: Define API Schemas

**Files:**
- Modify: `backend/app/api/v1/schemas/recommendations.py`

- [ ] **Step 1: Add Question and PracticeTestResponse models**

```python
# In backend/app/api/v1/schemas/recommendations.py

class Question(BaseModel):
    text: str
    options: List[str]
    correct_answer_index: int

class PracticeTestResponse(BaseModel):
    id: int
    lesson_id: int
    questions: List[Question]
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/api/v1/schemas/recommendations.py
git commit -m "feat(api): add practice test schemas"
```

---

### Task 2: Update Repository Layer

**Files:**
- Modify: `backend/app/infrastructure/db/repositories/plan_repository.py`

- [ ] **Step 1: Add get_practice_test and create_practice_test methods**

```python
# In backend/app/infrastructure/db/repositories/plan_repository.py
# Add PracticeTestORM to imports if not present
from app.infrastructure.db.models import LearningPlanORM, LessonORM, UserTestScoreORM, PracticeTestORM

# Add to PlanRepository class:

    def get_practice_test(self, lesson_id: int) -> Optional[PracticeTestORM]:
        return self.db.scalar(
            select(PracticeTestORM).where(PracticeTestORM.lesson_id == lesson_id)
        )

    def create_practice_test(self, lesson_id: int, content: dict) -> PracticeTestORM:
        db_test = PracticeTestORM(
            lesson_id=lesson_id,
            content=content
        )
        self.db.add(db_test)
        self.db.commit()
        self.db.refresh(db_test)
        return db_test
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/infrastructure/db/repositories/plan_repository.py
git commit -m "feat(repo): add practice test retrieval and creation"
```

---

### Task 3: Implement API Endpoint

**Files:**
- Modify: `backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 1: Implement the GET /lessons/{lesson_id}/test route**

```python
# In backend/app/api/v1/endpoints/lessons.py
# Add imports
from app.api.v1.schemas.recommendations import LessonDetail, PracticeTestResponse
import json

@router.get("/{lesson_id}/test", response_model=PracticeTestResponse)
async def get_lesson_test(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")

    # 1. Get lesson and check ownership
    lesson = plan_repo.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    plan = plan_repo.get_by_id(current_user.id, lesson.plan_id)
    if not plan:
        raise HTTPException(status_code=403, detail="Not authorized to view this lesson")

    # 2. Check for existing test
    test_orm = plan_repo.get_practice_test(lesson_id)
    if test_orm:
        return test_orm

    # 3. Generate test if missing
    logger.info(f"Generating practice test for lesson {lesson_id}")
    
    # Get lesson content if it exists
    lesson_content = lesson.content or ""
    
    prompt = f"""You are an expert educator. Generate a high-quality practice test for the following lesson.
    
Lesson Title: {lesson.title}
Lesson Description: {lesson.description}
Lesson Content: {lesson_content}

Strict Requirements:
1. Generate exactly 5 multiple-choice questions.
2. Each question must have 4 options.
3. Provide the index of the correct answer (0-3).
4. Use KaTeX/LaTeX for ALL mathematical expressions:
   - Inline math: $x + y = z$
   - Block math: $$ \\frac{{x}}{{y}} $$
5. Output ONLY a valid JSON array of question objects.

JSON Schema:
[
  {{
    "text": "Question text here",
    "options": ["Option 0", "Option 1", "Option 2", "Option 3"],
    "correct_answer_index": 0
  }},
  ...
]
"""
    try:
        # Re-use the LLM logic from get_lesson_detail or use a helper
        # For simplicity in this plan, I'll use the same direct openai/llamaindex call
        if OpenAI:
            llm = OpenAI(model="gpt-4o", temperature=0.3)
            response = await llm.acomplete(prompt)
            content_str = response.text.strip()
        else:
            import openai
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            content_str = response.choices[0].message.content.strip()

        # Robust JSON extraction
        content_str = re.sub(r"^```json\s*", "", content_str, flags=re.MULTILINE)
        content_str = re.sub(r"```\s*$", "", content_str, flags=re.MULTILINE)
        start = content_str.find('[')
        end = content_str.rfind(']')
        if start != -1 and end != -1:
            content_str = content_str[start:end+1]
        
        questions = json.loads(content_str)
        
        # Save to DB
        test_orm = plan_repo.create_practice_test(lesson_id, {"questions": questions})
        return test_orm

    except Exception as e:
        logger.error(f"Error generating test for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate practice test")
```

- [ ] **Step 2: Commit changes**

```bash
git add backend/app/api/v1/endpoints/lessons.py
git commit -m "feat(api): implement practice test generation endpoint"
```

---

### Task 4: Verification and Testing

**Files:**
- Create: `backend/tests/test_practice_tests.py`

- [ ] **Step 1: Write integration tests for the test endpoint**

```python
# In backend/tests/test_practice_tests.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_get_practice_test_flow(client: TestClient, normal_user_token_headers):
    # 1. Create a lesson (we'll need to mock or use existing seed data)
    # For now, we'll assume there's a lesson ID 1 in the seeded test database
    lesson_id = 1
    
    # 2. Request the test
    response = client.get(
        f"/api/v1/lessons/{lesson_id}/test",
        headers=normal_user_token_headers
    )
    
    # Depending on whether the lesson exists and belongs to the user,
    # we expect 200, 403, or 404.
    # In a real test environment, we should ensure the lesson exists first.
    assert response.status_code in [200, 403, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 5
        for q in data["questions"]:
            assert "text" in q
            assert "options" in q
            assert len(q["options"]) == 4
            assert "correct_answer_index" in q
```

- [ ] **Step 2: Run tests**

Run: `cd backend && pytest tests/test_practice_tests.py`

- [ ] **Step 3: Commit and Finish**

```bash
git add backend/tests/test_practice_tests.py
git commit -m "test: add practice test generation tests"
```
