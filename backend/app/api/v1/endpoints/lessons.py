from fastapi import APIRouter, Depends, HTTPException, Body
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
    service: LessonService = Depends(get_lesson_service)
):
    lesson = await service.get_lesson_detail(current_user, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found or access denied")
    return lesson

@router.patch("/{lesson_id}")
async def update_lesson(
    lesson_id: int,
    status_update: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_active_user),
    service: LessonService = Depends(get_lesson_service)
):
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    success = service.update_lesson_status(current_user, lesson_id, new_status)
    if not success:
        raise HTTPException(status_code=404, detail="Lesson not found or access denied")
    
    return {"message": "Status updated"}

@router.get("/{lesson_id}/test", response_model=PracticeTestResponse)
async def get_lesson_test(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    service: LessonService = Depends(get_lesson_service)
):
    test = await service.get_practice_test(current_user, lesson_id)
    if not test:
        raise HTTPException(status_code=404, detail="Practice test not found or generation failed")
    return test

@router.post("/{lesson_id}/test/submit", response_model=TestSubmissionResponse)
async def submit_lesson_test(
    lesson_id: int,
    submission: TestSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    service: LessonService = Depends(get_lesson_service)
):
    result = service.submit_test(current_user, lesson_id, submission)
    if not result:
        raise HTTPException(status_code=404, detail="Test submission failed or lesson not found")
    return result
