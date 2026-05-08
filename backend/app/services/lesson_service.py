import logging
import json
import re
from typing import Optional, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LearningPlanORM, LessonORM
from app.api.v1.schemas.recommendations import (
    LessonDetail,
    PracticeTestResponse,
    TestSubmissionRequest,
    TestSubmissionResponse,
    TestSubmissionResultItem,
)
from app.domain.identity.entities import User

LlamaOpenAI: Any = None
try:
    from llama_index.llms.openai import OpenAI

    LlamaOpenAI = OpenAI
except ImportError:
    pass

logger = logging.getLogger(__name__)


class LessonService:
    def __init__(self, plan_repo: PlanRepository, db: Session):
        self.plan_repo = plan_repo
        self.db = db

    async def get_lesson_detail(self, user: User, lesson_id: int) -> Optional[LessonDetail]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
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
                if LlamaOpenAI:
                    llm = LlamaOpenAI(model="gpt-4o", temperature=0.3)
                    response = await llm.acomplete(prompt)
                    content = response.text.strip() if response.text else ""
                else:
                    import openai

                    client = openai.AsyncOpenAI()
                    response = await client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                    )
                    content = (
                        response.choices[0].message.content.strip()
                        if response.choices[0].message.content
                        else ""
                    )

                lesson_orm = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
                if lesson_orm:
                    lesson_orm.content = content
                    self.db.commit()

            except Exception as e:
                logger.error(f"Error generating content for lesson {lesson_id}: {e}")

        lesson_detail = self.plan_repo.get_lesson_with_materials(user.id, lesson.plan_id, lesson_id)
        return lesson_detail

    def update_lesson_status(self, user: User, lesson_id: int, new_status: str) -> bool:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        lesson = self.db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
        if not lesson:
            return False

        # Check ownership
        plan_orm = self.db.scalar(
            select(LearningPlanORM)
            .where(LearningPlanORM.id == lesson.plan_id)
            .where(LearningPlanORM.user_id == user.id)
        )
        if not plan_orm:
            raise HTTPException(status_code=403, detail="Not authorized")

        if new_status == "completed":
            self.plan_repo.complete_lesson(user.id, lesson_id)
        else:
            lesson.status = new_status
            self.db.commit()

        self.plan_repo.touch_plan(lesson.plan_id)
        return True

    async def get_practice_test(self, user: User, lesson_id: int) -> Optional[PracticeTestResponse]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # 1. Get lesson and check ownership
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
            raise HTTPException(status_code=403, detail="Not authorized to view this lesson")

        # 2. Check for existing test
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if test_orm:
            return PracticeTestResponse(
                id=test_orm.id,
                lesson_id=test_orm.lesson_id,
                questions=test_orm.content["questions"],
            )

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
            if LlamaOpenAI:
                llm = LlamaOpenAI(model="gpt-4o", temperature=0.3)
                response = await llm.acomplete(prompt)
                content_str = response.text.strip() if response.text else ""
            else:
                import openai

                client = openai.AsyncOpenAI()
                response = await client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.3
                )
                content_str = (
                    response.choices[0].message.content.strip()
                    if response.choices[0].message.content
                    else ""
                )

            # Robust JSON extraction
            content_str = re.sub(r"^```json\s*", "", content_str, flags=re.MULTILINE)
            content_str = re.sub(r"```\s*$", "", content_str, flags=re.MULTILINE)
            start = content_str.find("[")
            end = content_str.rfind("]")
            if start != -1 and end != -1:
                content_str = content_str[start : end + 1]

            questions = json.loads(content_str)

            # Save to DB
            test_orm = self.plan_repo.create_practice_test(lesson_id, {"questions": questions})
            return PracticeTestResponse(
                id=test_orm.id,
                lesson_id=test_orm.lesson_id,
                questions=test_orm.content["questions"],
            )

        except Exception as e:
            logger.error(f"Error generating test for lesson {lesson_id}: {e}")
            return None

    def submit_test(
        self, user: User, lesson_id: int, submission: TestSubmissionRequest
    ) -> Optional[TestSubmissionResponse]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # 1. Get lesson and check ownership
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 2. Get the test
        test_orm = self.plan_repo.get_practice_test(lesson_id)
        if not test_orm:
            return None

        questions = test_orm.content["questions"]
        results = []
        correct_count = 0

        for i, q in enumerate(questions):
            submitted_idx = submission.answers[i] if i < len(submission.answers) else -1
            is_correct = submitted_idx == q["correct_answer_index"]
            if is_correct:
                correct_count += 1

            results.append(
                TestSubmissionResultItem(
                    question_index=i,
                    is_correct=is_correct,
                    correct_answer_index=q["correct_answer_index"],
                    explanation=q["explanation"],
                )
            )

        # 3. Save score as percentage
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user.id, lesson_id, score_percentage)

        # 4. Mark lesson as completed and unlock next one
        self.plan_repo.complete_lesson(user.id, lesson_id)

        return TestSubmissionResponse(score=correct_count, total=len(questions), results=results)
