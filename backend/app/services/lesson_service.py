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

    async def _review_typing_answer_with_ai(self, question: dict, user_answer: Any) -> bool:
        if not isinstance(user_answer, str) or not user_answer.strip():
            return False

        correct_answer = question.get("correct_answer_text", "")
        question_text = question.get("question", "")

        prompt = f"""You are an expert grading assistant. Review if the student's answer is factually correct and equivalent to the correct answer for the following question.

Question: {question_text}
Correct Answer: {correct_answer}
Student's Answer: {user_answer}

Consider synonyms, spelling variations, minor typos, or slight variations in wording as correct.
Output ONLY "YES" if the student's answer is correct/acceptable, or "NO" if it is wrong.
No explanation, no markdown.
"""
        try:
            from app.infrastructure.ai.model_factory import get_model
            llm = get_model()
            response = await llm.acomplete(prompt)
            result = response.text.strip().upper()
            
            # Strip any non-alphabet characters
            result = re.sub(r"[^A-Z]", "", result)
            
            if "YES" in result:
                logger.info(f"AI review marked answer '{user_answer}' as CORRECT for question '{question_text}'")
                return True
            else:
                logger.info(f"AI review marked answer '{user_answer}' as INCORRECT for question '{question_text}'")
                return False
        except Exception as e:
            logger.error(f"Error during AI review of typing question: {e}")
            return False

    async def get_practice_test(self, user: User, lesson_id: int) -> Optional[PracticeTestResponse]:
        if user.id is None:
            raise HTTPException(status_code=401, detail="User ID not found")

        # 1. Get lesson and check ownership
        lesson = self.plan_repo.get_lesson(lesson_id)
        if not lesson:
            return None

        plan = self.plan_repo.get_by_id(user.id, lesson.plan_id)
        if not plan:
            raise HTTPException(status_code=403, detail="Not authorized to view this test")

        # 2. Check if a test already exists
        test_orm = self.plan_repo.get_practice_test(lesson_id)

        # 3. Generate test if it doesn't exist
        if not test_orm:
            logger.info(f"Generating practice test for lesson {lesson_id}")
            lesson_content = lesson.content or ""
            language = plan.language if hasattr(plan, "language") else "en"
            
            prompt = f"""You are an expert educator. Generate a practice test with EXACTLY 10 questions based on this lesson:
Title: {lesson.title}
Description: {lesson.description}
Content: {lesson_content}

Generate a balanced mix of:
1. "multiple_choice" (4 options, correct_answer_index 0-3)
2. "true_false" (2 options, correct_answer_index 0-1)
3. "short_answer" (correct_answer_text)
4. "fill_in_the_blank" (correct_answer_text)

You MUST respond with a raw JSON array matching this format EXACTLY:
[
  {{
    "type": "multiple_choice",
    "question": "Question text?",
    "options": ["Opt 1", "Opt 2", "Opt 3", "Opt 4"],
    "correct_answer_index": 1,
    "explanation": "Brief explanation..."
  }},
  {{
    "type": "short_answer",
    "question": "Question text?",
    "correct_answer_text": "Expected answer text",
    "explanation": "Brief explanation..."
  }}
]

OUTPUT LANGUAGE: You MUST provide all text content (questions, options, explanations) in the following language: {language}.
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

                content_str = re.sub(r"^```json\s*", "", content_str, flags=re.MULTILINE)
                content_str = re.sub(r"```\s*$", "", content_str, flags=re.MULTILINE)
                start = content_str.find("[")
                end = content_str.rfind("]")
                if start != -1 and end != -1:
                    content_str = content_str[start : end + 1]

                questions = json.loads(content_str)
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
            ai_reviews = last_score.answers.get("ai_reviews", {})
            results = []
            for i, q in enumerate(questions):
                submitted = prev_answers[i] if i < len(prev_answers) else None
                
                # Check for cached AI review result
                if str(i) in ai_reviews:
                    is_correct = ai_reviews[str(i)]
                elif i < len(prev_answers) and isinstance(ai_reviews, dict) and i in ai_reviews:
                    is_correct = ai_reviews[i]
                else:
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

    async def submit_test(
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
        ai_reviews = {}

        for i, q in enumerate(questions):
            submitted = submission.answers[i] if i < len(submission.answers) else None
            is_correct = self._grade_question(q, submitted)
            
            # If exact match failed, but it is a short answer/fill in the blank, review with AI
            q_type = q.get("type", "multiple_choice")
            if not is_correct and q_type in ["short_answer", "fill_in_the_blank"] and submitted:
                is_correct = await self._review_typing_answer_with_ai(q, submitted)

            ai_reviews[str(i)] = is_correct

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

        # 3. Save score as percentage and save ai_reviews
        score_percentage = int((correct_count / len(questions)) * 100) if questions else 0
        self.plan_repo.save_test_score(
            user.id, lesson_id, score_percentage, submission.answers, ai_reviews=ai_reviews
        )

        # 4. Mark lesson as completed and unlock next one
        self.plan_repo.complete_lesson(user.id, lesson_id)

        return TestSubmissionResponse(score=correct_count, total=len(questions), results=results)

    async def check_answer(
        self, user: User, lesson_id: int, request: Any
    ) -> Optional[dict]:
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
        q_idx = request.question_index
        if q_idx < 0 or q_idx >= len(questions):
            return None

        q = questions[q_idx]
        submitted = request.answer
        is_correct = self._grade_question(q, submitted)

        # AI review for short answer or fill in the blank questions if exact match failed
        q_type = q.get("type", "multiple_choice")
        if not is_correct and q_type in ["short_answer", "fill_in_the_blank"] and submitted:
            is_correct = await self._review_typing_answer_with_ai(q, submitted)

        return {
            "is_correct": is_correct,
            "correct_answer_text": q.get("correct_answer_text") if not is_correct else None,
            "explanation": q.get("explanation"),
        }
