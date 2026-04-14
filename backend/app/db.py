import os
import time
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .models import Base, CourseORM, UserORM, Course

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://advisor:advisor_password@db:5432/course_advisor")

# Connection retry logic
MAX_RETRIES = 5
RETRY_DELAY = 2

engine = None

# Only attempt connection if not in a test environment
if os.getenv("TESTING") != "1":
    for i in range(MAX_RETRIES):
        try:
            engine = create_engine(DATABASE_URL)
            # Test connection
            with engine.connect() as conn:
                pass
            logger.info("Successfully connected to the database")
            break
        except OperationalError as e:
            if i == MAX_RETRIES - 1:
                logger.error(f"Could not connect to database after {MAX_RETRIES} attempts")
                raise e
            logger.warning(f"Database connection attempt {i+1} failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
else:
    # Use in-memory SQLite for tests if DATABASE_URL is not provided or if testing
    engine = create_engine("sqlite:///:memory:")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Migration helpers (will use ORM versions of old functions)
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
