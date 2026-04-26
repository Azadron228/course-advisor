from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user, get_service
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.api.v1.schemas.course import CoursePublic
from app.domain.identity.entities import User

router = APIRouter()

@router.get("/{course_id}", response_model=CoursePublic)
async def get_course_by_id(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    course_repo: CourseRepository = Depends(get_service(CourseRepository))
):
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
