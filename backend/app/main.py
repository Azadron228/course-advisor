from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from .models import Student, UserPreference, RecommendationResponse, TranscriptEntry, ModelProvider
from .scoring.orchestrator import HybridScorer
from .parser import parse_transcript_html
from .db import get_all_courses
from typing import List

app = FastAPI()
scorer = HybridScorer()

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference
):
    courses = get_all_courses()
    if not courses:
         # Return empty instead of error, Task 9 will add seed data
         return RecommendationResponse(results=[])
    # Defaulting to AUTO since it was removed from query
    return await scorer.recommend(student, courses, preference, provider=ModelProvider.AUTO)

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
