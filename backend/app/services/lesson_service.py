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
from app.infrastructure.ai.tavily_search import TavilySearch

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
        self.search_client = TavilySearch()

    def _grade_question(self, question: dict, submitted: Any) -> bool:
        q_type = question.get("type", "multiple_choice")
        if q_type in ["multiple_choice", "true_false"]:
            return submitted == question.get("correct_answer_index")
        elif q_type in ["short_answer", "fill_in_the_blank"]:
            if isinstance(submitted, str) and question.get("correct_answer_text"):
                return submitted.strip().lower() == question["correct_answer_text"].strip().lower()
        return False

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
            
            language = plan.language if hasattr(plan, "language") else "en"
            
            # Use Tavily to get context
            search_query = f"{lesson.title} {lesson.description}"
            logger.info(f"Searching Tavily for: {search_query}")
            search_context = await self.search_client.get_search_context(search_query)

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
- OUTPUT LANGUAGE: You MUST provide all content in the following language: {language}.

Title: {lesson.title}
Description: {lesson.description}

{search_context}
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
        
        if not test_orm:
            # 3. Generate test if missing
            logger.info(f"Generating practice test for lesson {lesson_id}")

            # Get lesson content if it exists
            lesson_content = lesson.content or ""
            language = plan.language if hasattr(plan, "language") else "en"

            prompt = f"""You are an expert educator. Generate a high-quality practice test for the following lesson.
    
Lesson Title: {lesson.title}
Lesson Description: {lesson.description}
Lesson Content: {lesson_content}

Strict Requirements:
1. Generate between 8 and 10 questions of various types:
   - multiple_choice: 4 options, 1 correct index.
   - short_answer: concise text answer (1-3 words).
   - true_false: 2 options (True, False), 1 correct index.
   - fill_in_the_blank: question with a "____" placeholder, concise text answer (1-3 words).
2. Distribute types relatively evenly.
3. Provide a brief explanation of why the answer is correct.
4. Use KaTeX/LaTeX for ALL mathematical expressions:
   - Inline math: $x + y = z$
   - Block math: $$ \\frac{{x}}{{y}} $$
5. Output ONLY a valid JSON array of question objects.
6. OUTPUT LANGUAGE: You MUST provide all text content (questions, options, explanations) in the following language: {language}.

JSON Schema for each object:
{{
  "type": "multiple_choice" | "short_answer" | "true_false" | "fill_in_the_blank",
  "question": "Question text here",
  "options": ["Option 0", "Option 1", ...] (for multiple_choice and true_false ONLY),
  "correct_answer_index": index (for multiple_choice and true_false ONLY),
  "correct_answer_text": "text" (for short_answer and fill_in_the_blank ONLY),
  "explanation": "Explanation here"
}}
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
            except Exception as e:
                logger.error(f"Error generating test for lesson {lesson_id}: {e}")
                return None

        # 4. Get last attempt if it exists
        last_score = self.plan_repo.get_last_test_score(user.id, lesson_id)
        last_attempt = None
        if last_score and last_score.answers:
            questions = test_orm.content["questions"]
            prev_answers = last_score.answers.get("answers", [])
            results = []
            for i, q in enumerate(questions):
                submitted = prev_answers[i] if i < len(prev_answers) else None
                is_correct = self._grade_question(q, submitted)
                results.append(
                    TestSubmissionResultItem(
                        question_index=i,
                        is_correct=is_correct,
                        user_answer=submitted,
                        correct_answer_index=q.get("correct_answer_index"),
                        correct_answer_text=q.get("correct_answer_text"),
                        explanation=q["explanation"],
                    )
                )
            
            last_attempt = TestSubmissionResponse(
                score=int((last_score.score / 100) * len(questions)),
                total=len(questions),
                results=results
            )

        return PracticeTestResponse(
            id=test_orm.id,
            lesson_id=test_orm.lesson_id,
            questions=test_orm.content["questions"],
            last_attempt=last_attempt
        )

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
            submitted = submission.answers[i] if i < len(submission.answers) else None
            is_correct = self._grade_question(q, submitted)
            
            if is_correct:
                correct_count += 1

            results.append(
                TestSubmissionResultItem(
                    question_index=i,
                    is_correct=is_correct,
                    user_answer=submitted,
                    correct_answer_index=q.get("correct_answer_index"),
                    correct_answer_text=q.get("correct_answer_text"),
                    explanation=q["explanation"],
                )
            )

        # 3. Save score as percentage
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(user.id, lesson_id, score_percentage, submission.answers)

        # 4. Mark lesson as completed and unlock next one
        self.plan_repo.complete_lesson(user.id, lesson_id)

        return TestSubmissionResponse(score=correct_count, total=len(questions), results=results)
