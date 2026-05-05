from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.api.deps import get_current_active_user, get_service, get_db
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LearningPlanORM, LessonORM
from app.api.v1.schemas.recommendations import LessonDetail, PracticeTestResponse
from app.domain.identity.entities import User
from typing import Dict
import logging
import json
import re

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None
    import openai

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson_detail(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    lesson = plan_repo.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    plan = plan_repo.get_by_id(current_user.id, lesson.plan_id)
    if not plan:
        raise HTTPException(status_code=403, detail="Not authorized to view this lesson")
        
    if not lesson.content:
        logger.info(f"Generating content for lesson {lesson_id} in real time")
        
        prompt = f"""You are an expert academic educator. Generate a comprehensive, well-structured lesson in strict Markdown format.

## Strict Formatting Rules:
- Use `#` for title, `##` for sections, `###` for subsections
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

            lesson_orm = db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
            if lesson_orm:
                lesson_orm.content = content
                db.commit()
            
        except Exception as e:
            logger.error(f"Error generating content for lesson {lesson_id}: {e}")
            # Do not raise, just let it return None for content

    lesson_detail = plan_repo.get_lesson_with_materials(current_user.id, lesson.plan_id, lesson_id)
    if not lesson_detail:
        raise HTTPException(status_code=404, detail="Lesson detail not found")
        
    return lesson_detail

@router.patch("/{lesson_id}")
async def update_lesson(
    lesson_id: int,
    status_update: Dict[str, str] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    plan_repo: PlanRepository = Depends(get_service(PlanRepository))
):
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="User ID not found")
        
    lesson = db.scalar(select(LessonORM).where(LessonORM.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Check ownership
    plan_orm = db.scalar(select(LearningPlanORM).where(LearningPlanORM.id == lesson.plan_id).where(LearningPlanORM.user_id == current_user.id))
    if not plan_orm:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    lesson.status = new_status
    
    # Auto-unlock next step if completed
    if new_status == "completed":
        plan = db.scalar(
            select(LearningPlanORM)
            .options(selectinload(LearningPlanORM.lessons))
            .where(LearningPlanORM.id == lesson.plan_id)
        )
        if plan:
            found_idx = -1
            for i, lesson_orm in enumerate(plan.lessons):
                if lesson_orm.id == lesson.id:
                    found_idx = i
                    break
            
            if found_idx != -1 and found_idx + 1 < len(plan.lessons):
                next_lesson = plan.lessons[found_idx + 1]
                if next_lesson.status == "upcoming":
                    next_lesson.status = "current"
        
    db.commit()
    plan_repo.touch_plan(lesson.plan_id)
    return {"message": "Status updated"}

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
        return {
            "id": test_orm.id,
            "lesson_id": test_orm.lesson_id,
            "questions": test_orm.content["questions"]
        }

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
        return {
            "id": test_orm.id,
            "lesson_id": test_orm.lesson_id,
            "questions": test_orm.content["questions"]
        }

    except Exception as e:
        logger.error(f"Error generating test for lesson {lesson_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate practice test")
