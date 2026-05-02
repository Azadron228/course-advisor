import io
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.api.deps import get_db, get_current_admin_user
from app.infrastructure.db.repositories.course_repository import CourseRepository
from app.api.v1.schemas.course import CoursePublic, CourseCreate, CourseUpdate, CourseMaterialPublic
from app.infrastructure.ai.embeddings import get_embedding
from app.domain.catalog.entities import Course as CourseEntity, CourseMaterial as CourseMaterialEntity

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/courses", response_model=list[CoursePublic])
async def list_courses(
    db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    return course_repo.get_all()


@router.post("/courses", response_model=CoursePublic)
async def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
):
    course_repo = CourseRepository(db)

    # Generate initial embedding
    embedding = get_embedding(course_in.description)

    # Create Course Entity
    course = CourseEntity(**course_in.model_dump(), embedding=embedding, id=0)

    saved_course = course_repo.save(course)
    return saved_course


@router.put("/courses/{course_id}", response_model=CoursePublic)
async def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
):
    course_repo = CourseRepository(db)
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = course_in.model_dump(exclude_unset=True)

    # Create new course object with updated values
    from dataclasses import replace

    updated_course = replace(course, **update_data)

    # Recalculate embedding if description changed
    if "description" in update_data:
        updated_course = replace(
            updated_course, embedding=get_embedding(updated_course.description)
        )

    saved_course = course_repo.save(updated_course)
    return saved_course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)
):
    course_repo = CourseRepository(db)
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_repo.delete(course_id)
    return None


# Course Materials


@router.post("/courses/{course_id}/materials", response_model=CourseMaterialPublic)
async def upload_course_materials(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
    arq_pool = Depends(deps.get_arq_pool),
):
    course_repo = CourseRepository(db)
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    content = ""
    filename = file.filename or "unknown"
    if filename.endswith(".pdf"):
        if PyPDF2 is None:
            raise HTTPException(status_code=500, detail="PyPDF2 not installed")
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
            for page in pdf_reader.pages:
                content += page.extract_text()
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    else:
        # Assume text/plain
        content = (await file.read()).decode("utf-8")

    # Sanitize content (PostgreSQL does not allow NUL characters)
    content = content.replace("\x00", "")

    # Create material entity
    material = CourseMaterialEntity(
        id=0,
        course_id=course_id,
        filename=filename,
        content=content,
        status="pending",
        created_at="",
    )

    saved_material = course_repo.add_material(material)

    # Enqueue background task for chunking and embedding
    await arq_pool.enqueue_job("process_material_embeddings", saved_material.id)

    return saved_material


@router.get("/courses/{course_id}/materials", response_model=list[CourseMaterialPublic])
async def list_course_materials(
    course_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
):
    course_repo = CourseRepository(db)
    course = course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.materials


@router.delete("/courses/{course_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_material(
    course_id: int,
    material_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user),
):
    course_repo = CourseRepository(db)
    material = course_repo.get_material(material_id)
    if not material or material.course_id != course_id:
        raise HTTPException(status_code=404, detail="Material not found")

    course_repo.delete_material(material_id)

    # Update embedding again (NOW ONLY USES DESCRIPTION)
    course = course_repo.get_by_id(course_id)
    new_embedding = get_embedding(course.description)

    from dataclasses import replace
    updated_course = replace(course, embedding=new_embedding)
    course_repo.save(updated_course)

    return None
