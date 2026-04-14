from datetime import timedelta
from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .schemas.course import Student, UserPreference, TranscriptEntry
from .schemas.recommendation import RecommendationResponse
from .schemas.internal import ModelProvider
from .schemas.user import UserBase as User, UserCreate, UserInDB
from .schemas.token import Token
from .models import UserORM
from .scoring.orchestrator import HybridScorer
from .parser import parse_transcript_html
from .db import get_all_courses, get_user_by_email, create_user, get_db
from .auth import authenticate_user, get_current_active_user
from .core.config import settings
from .core.security import get_password_hash, create_access_token
from typing import List
import os
import redis
from rq import Queue
from rq.job import Job

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scorer = HybridScorer()

# Redis connection
redis_conn = redis.from_url(settings.REDIS_URL)
q = Queue(connection=redis_conn)

# --- Auth Endpoints ---

@app.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    create_user(db, user.email, hashed_password, user.full_name)
    return User(email=user.email, full_name=user.full_name)

@app.post("/token", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm.username will contain the email entered by the user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Application Endpoints ---

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    courses = get_all_courses(db)
    if not courses:
         return RecommendationResponse(results=[])
    return await scorer.recommend(db, student, courses, preference, provider=ModelProvider.AUTO)

from .jobs import run_hybrid_recommendation

@app.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: Student,
    preference: UserPreference,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    job = q.enqueue(
        run_hybrid_recommendation,
        student.model_dump(),
        [c.model_dump() for c in get_all_courses(db)],
        preference.model_dump()
    )
    return {"job_id": job.get_id()}

@app.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result if job.is_finished else None,
        "enqueued_at": job.enqueued_at,
        "started_at": job.started_at,
        "ended_at": job.ended_at
    }

@app.post("/parse-transcript", response_model=List[TranscriptEntry])
async def parse_transcript(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Only HTML files are supported")
    
    content = await file.read()
    try:
        html_content = content.decode('utf-8')
    except UnicodeDecodeError:
        html_content = content.decode('latin-1')
        
    return parse_transcript_html(html_content)
