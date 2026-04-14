from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import CourseORM, UserORM

def get_all_courses(db: Session):
    from .models import Course as CourseModel
    orms = db.scalars(select(CourseORM)).all()
    courses = []
    for o in orms:
        # Handle skills_taught which might be stored as a list or a JSON string in some setups
        skills = o.skills_taught
        if isinstance(skills, str):
            import json
            skills = json.loads(skills)
        if not isinstance(skills, list):
            skills = []
            
        courses.append(CourseModel(
            id=o.id,
            subject_name=o.subject_name,
            credits=o.credits,
            description=o.description,
            skills_taught=skills,
            difficulty=o.difficulty if o.difficulty is not None else 0.0,
            workload=o.workload if o.workload is not None else 0.0,
            prerequisites=[]
        ))
    return courses

def get_user_by_email(db: Session, email: str):
    return db.scalar(select(UserORM).where(UserORM.email == email))

def create_user(db: Session, email: str, hashed_password: str, full_name: str = None):
    db_user = UserORM(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
