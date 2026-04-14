from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from ...crud import get_all_courses
from ..deps import get_db, get_current_admin_user

router = APIRouter()

@router.get("/courses", response_model=list[CoursePublic])
async def read_courses(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    return get_all_courses(db)

@router.put("/courses/{course_id}", response_model=CoursePublic)
async def update_course(
    course_id: str,
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course = db.scalar(select(CourseORM).where(CourseORM.id == course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course = db.scalar(select(CourseORM).where(CourseORM.id == course_id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return None
