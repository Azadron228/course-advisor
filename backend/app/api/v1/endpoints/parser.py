from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api.v1.schemas.recommendations import TranscriptEntry
from app.infrastructure.ai.parser import parse_transcript_html
from app.api.deps import get_current_active_user
from app.domain.identity.entities import User

router = APIRouter()


@router.post("/parse-transcript", response_model=List[TranscriptEntry])
async def parse_transcript(
    file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)
):
    if not file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="Only HTML files are supported")

    content = await file.read()
    try:
        html_content = content.decode("utf-8")
    except UnicodeDecodeError:
        html_content = content.decode("latin-1")

    return parse_transcript_html(html_content)
