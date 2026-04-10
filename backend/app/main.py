from fastapi import FastAPI, HTTPException, Body
from  app.models import Student, UserPreference, RecommendationResponse, TranscriptEntry, ModelProvider
from  app.scoring.orchestrator import HybridScorer
from  app.parser import parse_transcript_html
from  app.db import get_all_courses
from typing import List

app = FastAPI()
scorer = HybridScorer()

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    student: Student, 
    preference: UserPreference,
    model_provider: ModelProvider = ModelProvider.AUTO
):
    courses = get_all_courses()
    if not courses:
         # Return empty instead of error, Task 9 will add seed data
         return RecommendationResponse(results=[])
    return await scorer.recommend(student, courses, preference, provider=model_provider)

@app.post("/parse-transcript", response_model=List[TranscriptEntry])
async def parse_transcript(payload: dict = Body(...)):
    html = payload.get("html", "")
    if not html:
        raise HTTPException(status_code=400, detail="HTML content is required")
    return parse_transcript_html(html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
