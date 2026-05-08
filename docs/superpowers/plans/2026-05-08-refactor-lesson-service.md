# Refactor Lesson Logic into LessonService Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move business logic for lesson content generation, practice test generation, and test submission from the API endpoint to a dedicated `LessonService` for better maintainability and testability.

**Architecture:** Create `LessonService` in `app.services`, register it in the dependency injection container (`punq`), and update the API endpoints to use the service.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Punq (DI), Pydantic, AI (OpenAI/LlamaIndex).

---

### Task 1: Create LessonService

**Files:**
- Create: `backend/app/services/lesson_service.py`

- [ ] **Step 1: Implement LessonService with get_lesson_detail**

```python
import logging
import json
import re
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LessonORM
from app.api.v1.schemas.recommendations import (
    LessonDetail, 
    PracticeTestResponse, 
    TestSubmissionRequest, 
    TestSubmissionResponse,
    TestSubmissionResultItem
)

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

class LessonService:
    def __init__(self, plan_repo: PlanRepository, db: Session):
        self.plan_repo = plan_repo
        self.db = db

    async def get_lesson_detail(self, user_id: int, lesson_id: int) -> LessonDetail:
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson not found")
            
        plan = self.plan_repo.get_by_id(user_id, lesson.plan_id)
        if not plan:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to view this lesson")
            
        if not lesson.content:
            logger.info(f"Generating content for lesson {lesson_id} in real time")
            
            prompt = f"""You are an expert academic educator. Generate a comprehensive, well-structured lesson in strict Markdown format.

## Strict Formatting Rules:
- Use `#` for title, `##` for sections, `###` for subsections
- The main `#` title MUST be SHORT and MATCH the lesson title provided below.
- Use **bold** for key terms
- Use bullet and numbered lists where appropriate
- For ALL mathematical expressions use KaTeX/LaTeX syntax ONLY:
  - Inline math: wrap in single dollar signs: $x + y = z$
  - Block math: wrap in double dollar signs on their own line:
    $$
    \\frac{{x}}{{2}} + \\frac{{3}}{{4}} = \\frac{{2x+3}}{{4}}
    $$
- NEVER use [ ] or \\[ \\] for math — always use $ or $$
- Do NOT wrap output in ```markdown``` or any code block
- Start directly with the # title, no preamble

Title: {lesson.title}
Description: {lesson.description}
"""
            try:
                if OpenAI:
                    llm = OpenAI(model="gpt-4o", temperature=0.3)
                    response = await llm.acomplete(prompt)
                    content = response.text.strip()
                else:
                    import openai
                    client = openai.AsyncOpenAI()
                    response = await client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    content = response.choices[0].message.content.strip()

                lesson_orm = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
                if lesson_orm:
                    lesson_orm.content = content
                    self.db.commit()
                
            except Exception as e:
                logger.error(f"Error generating content for lesson {lesson_id}: {e}")

        lesson_detail = self.plan_repo.get_lesson_with_materials(user_id, lesson.plan_id, lesson_id)
        if not lesson_detail:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson detail not found")
            
        return lesson_detail

    async def get_practice_test(self, user_id: int, lesson_id: int) -> PracticeTestResponse:
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson not found")

        plan = self.plan_repo.get_by_id(user_id, lesson.plan_id)
        if not plan:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to view this lesson")

        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if test_orm:
            return PracticeTestResponse(
                id=test_orm.id,
                lesson_id=test_orm.lesson_id,
                questions=test_orm.content["questions"]
            )

        logger.info(f"Generating practice test for lesson {lesson_id}")
        lesson_content = lesson.content or ""
        
        prompt = f"""You are an expert educator. Generate a high-quality practice test for the following lesson.
    
Lesson Title: {lesson.title}
Lesson Description: {lesson.description}
Lesson Content: {lesson_content}

Strict Requirements:
1. Generate exactly 5 multiple-choice questions.
2. Each question must have 4 options.
3. Provide the index of the correct answer (0-3).
4. Provide a brief explanation of why the answer is correct.
5. Use KaTeX/LaTeX for ALL mathematical expressions:
   - Inline math: $x + y = z$
   - Block math: $$ \\frac{{x}}{{y}} $$
6. Output ONLY a valid JSON array of question objects.

JSON Schema:
[
  {{
    "question": "Question text here",
    "options": ["Option 0", "Option 1", "Option 2", "Option 3"],
    "correct_answer_index": 0,
    "explanation": "Explanation here"
  }},
  ...
]
"""
        try:
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

            content_str = re.sub(r"^```json\s*", "", content_str, flags=re.MULTILINE)
            content_str = re.sub(r"```\s*$", "", content_str, flags=re.MULTILINE)
            start = content_str.find('[')
            end = content_str.rfind(']')
            if start != -1 and end != -1:
                content_str = content_str[start:end+1]
            
            questions = json.loads(content_str)
            test_orm = self.plan_repo.create_practice_test(lesson_id, {"questions": questions})
            return PracticeTestResponse(
                id=test_orm.id,
                lesson_id=test_orm.lesson_id,
                questions=test_orm.content["questions"]
            )

        except Exception as e:
            logger.error(f"Error generating test for lesson {lesson_id}: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Failed to generate practice test")

    async def submit_test(self, user_id: int, lesson_id: int, submission: TestSubmissionRequest) -> TestSubmissionResponse:
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson not found")

        plan = self.plan_repo.get_by_id(user_id, lesson.plan_id)
        if not plan:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized")

        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if not test_orm:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="No practice test found for this lesson")

        questions = test_orm.content["questions"]
        results = []
        correct_count = 0

        for i, q in enumerate(questions):
            submitted_idx = submission.answers[i] if i < len(submission.answers) else -1
            is_correct = submitted_idx == q["correct_answer_index"]
            if is_correct:
                correct_count += 1
            
            results.append(TestSubmissionResultItem(
                question_index=i,
                is_correct=is_correct,
                correct_answer_index=q["correct_answer_index"],
                explanation=q["explanation"]
            ))

        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user_id, lesson_id, score_percentage)
        self.plan_repo.complete_lesson(user_id, lesson_id)

        return TestSubmissionResponse(
            score=correct_count,
            total=len(questions),
            results=results
        )

    def update_lesson_status(self, user_id: int, lesson_id: int, status: str):
        lesson = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
        if not lesson:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Lesson not found")
            
        from app.infrastructure.db.models import LearningPlanORM
        plan_orm = self.db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == lesson.plan_id).where(LearningPlanORM.user_id == user_id))
        if not plan_orm:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if status == "completed":
            self.plan_repo.complete_lesson(user_id, lesson_id)
        else:
            lesson.status = status
            self.db.commit()
        
        self.plan_repo.touch_plan(lesson.plan_id)
        return {"message": "Status updated"}
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/lesson_service.py
git commit -m "feat: implement LessonService"
```

---

### Task 2: Register LessonService in Container and Deps

**Files:**
- Modify: `backend/app/core/container.py`
- Modify: `backend/app/api/deps.py`

- [ ] **Step 1: Register LessonService in `backend/app/core/container.py`**

```python
# In backend/app/core/container.py
# Add import
from app.services.lesson_service import LessonService

# In get_container()
container.register(LessonService)
```

- [ ] **Step 2: Add `get_lesson_service` in `backend/app/api/deps.py`**

```python
# In backend/app/api/deps.py
# Add import
from app.services.lesson_service import LessonService

# Add helper
def get_lesson_service(service: LessonService = Depends(get_service(LessonService))):
    return service
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/core/container.py backend/app/api/deps.py
git commit -m "feat: register LessonService in DI container"
```

---

### Task 3: Refactor Lessons API Endpoints

**Files:**
- Modify: `backend/app/api/v1/endpoints/lessons.py`

- [ ] **Step 1: Update imports and use LessonService in endpoints**

```python
from fastapi import APIRouter, Depends, Body
from app.api.deps import get_current_active_user, get_lesson_service
from app.api.v1.schemas.recommendations import (
    LessonDetail, 
    PracticeTestResponse, 
    TestSubmissionRequest, 
    TestSubmissionResponse
)
from app.domain.identity.entities import User
from app.services.lesson_service import LessonService
from typing import Dict

router = APIRouter()

@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson_detail(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    lesson_service: LessonService = Depends(get_lesson_service)
):
    return await lesson_service.get_lesson_detail(current_user.id, lesson_id)

@router.patch("/{lesson_id}")
async def update_lesson(
    lesson_id: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    lesson_service: LessonService = Depends(get_lesson_service)
):
    new_status = status_update.get("status")
    from fastapi import HTTPException
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    return lesson_service.update_lesson_status(current_user.id, lesson_id, new_status)

@router.get("/{lesson_id}/test", response_model=PracticeTestResponse)
async def get_lesson_test(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    lesson_service: LessonService = Depends(get_lesson_service)
):
    return await lesson_service.get_practice_test(current_user.id, lesson_id)

@router.post("/{lesson_id}/test/submit", response_model=TestSubmissionResponse)
async def submit_lesson_test(
    lesson_id: int,
    submission: TestSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    lesson_service: LessonService = Depends(get_lesson_service)
):
    return await lesson_service.submit_test(current_user.id, lesson_id, submission)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/endpoints/lessons.py
git commit -m "refactor: use LessonService in lessons endpoints"
```

---

### Task 4: Update Tests

**Files:**
- Modify: `backend/tests/conftest.py`

- [ ] **Step 1: Register LessonService in `backend/tests/conftest.py` mock container**

```python
# In backend/tests/conftest.py
# Look for override_get_container
# Add LessonService registration
from app.services.lesson_service import LessonService
# ...
container.register(LessonService)
```

- [ ] **Step 2: Run tests to verify**

Run: `pytest backend/tests/test_practice_tests.py`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/tests/conftest.py
git commit -m "test: register LessonService in test container"
```
