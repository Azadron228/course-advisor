import time
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .models import Base, CourseORM, UserORM
from app.core.config import settings

logger = logging.getLogger(__name__)

# Connection retry logic
MAX_RETRIES = 5
RETRY_DELAY = 2

engine = None

# Only attempt connection if not in a test environment
if not settings.TESTING:
    for i in range(MAX_RETRIES):
        try:
            engine = create_engine(settings.DATABASE_URL)
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
    # Use in-memory SQLite for tests if testing
    engine = create_engine("sqlite:///:memory:")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
