from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from ...repositories.course import CourseRepository
from ..deps import get_db, get_current_admin_user
from ...models import CourseORM
from .schemas.course import CoursePublic, CourseCreate
from ...embeddings import get_embedding
import io
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

router = APIRouter()

@router.get("/courses", response_model=list[CoursePublic])
async def read_courses(
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    return course_repo.get_all()

@router.put("/courses/{course_id}", response_model=CoursePublic)
async def update_course(
    course_id: str,
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    course = course_repo.get_orm_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    # Recalculate embedding if description changed
    if "description" in update_data:
        course.embedding = get_embedding(course.description)
        
    course_repo.save(course)
    return course

@router.post("/courses/{course_id}/materials", response_model=CoursePublic)
async def upload_course_materials(
    course_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    course = course_repo.get_orm_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    content = ""
    filename = file.filename.lower()
    file_bytes = await file.read()
    
    if filename.endswith(".pdf"):
        if PyPDF2:
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail="PDF processing library not installed")
    else:
        # Assume text/plain or similar
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1")
            
    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be read")
        
    course.materials_content = content
    # Update embedding based on both description and materials for better retrieval
    combined_text = f"{course.description}\n\n{content[:5000]}" # Limit to first 5000 chars for embedding to avoid too large input
    course.embedding = get_embedding(combined_text)
    
    course_repo.save(course)
    return course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    course = course_repo.get_orm_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_repo.delete(course)
    return None
