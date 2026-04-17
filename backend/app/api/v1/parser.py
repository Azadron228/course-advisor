from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from .schemas.recommendations import TranscriptEntry
from .schemas.auth import UserPublic as User
from ...parser import parse_transcript_html
from ..deps import get_current_active_user

router = APIRouter()

@router.post("/parse-transcript", response_model=List[TranscriptEntry])
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
