from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from .models import Student, UserPreference, RecommendationResponse, TranscriptEntry, ModelProvider
from .scoring.orchestrator import HybridScorer
from .parser import parse_transcript_html
from .db import get_all_courses
from typing import List
import os
import redis
from rq import Queue
from rq.job import Job

app = FastAPI()
scorer = HybridScorer()

# Requirement: Add Redis connection via env REDIS_URL
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference
):
    # This remains synchronous/immediate for now as it calls scorer.recommend
    # which we might want to move to background if it's too slow.
    # However, the user specifically asked for "enqueue endpoints".
    courses = get_all_courses()
    if not courses:
         return RecommendationResponse(results=[])
    return await scorer.recommend(student, courses, preference, provider=ModelProvider.AUTO)

from .jobs import run_hybrid_recommendation
...
# Requirement: Expose enqueue endpoints, return job ID
@app.post("/enqueue-recommendation")
async def enqueue_recommendation(
    student: Student,
    preference: UserPreference
):
    # We'll enqueue the entire hybrid scoring process as it contains the agent runs
    job = q.enqueue(
        run_hybrid_recommendation,
        student.model_dump(),
        [c.model_dump() for c in get_all_courses()],
        preference.model_dump()
    )
    return {"job_id": job.get_id()}

# Requirement: Add job status/result polling endpoint
@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
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
async def parse_transcript(file: UploadFile = File(...)):
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Only HTML files are supported")
    
    content = await file.read()
    try:
        html_content = content.decode('utf-8')
    except UnicodeDecodeError:
        html_content = content.decode('latin-1') # Fallback
        
    return parse_transcript_html(html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
