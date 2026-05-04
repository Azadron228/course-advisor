from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.api.deps import get_current_active_user, get_service, get_db
from app.infrastructure.db.repositories.plan_repository import PlanRepository
from app.infrastructure.db.models import LearningPlanORM, LessonORM
from app.api.v1.schemas.recommendations import LessonDetail
from app.domain.identity.entities import User
from typing import Dict
import logging

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
        prompt = f"""You are an expert academic educator. Generate a comprehensive, high-quality, and easy-to-understand lesson based on the following title and description.
The lesson should be structured with clear headings (using Markdown), include key concepts, practical examples, and a summary.

Title: {lesson.title}
Description: {lesson.description}

Requirement: Provide ONLY the lesson content in Markdown format.
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
