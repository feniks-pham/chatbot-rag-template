import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.tts import TTSService
from app.utils.helpers import clean_markdown
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
tts_service = TTSService()

class TTSRequest(BaseModel):
    text: str

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        text = clean_markdown(request.text)
        audio_file = await tts_service.text_to_speech(text)
        
        # Create async cleanup function
        async def cleanup_file():
            try:
                os.unlink(audio_file)
                logger.info(f"Cleaned up temp file: {audio_file}")
            except Exception as exc:
                logger.error(f"Error cleaning up file {audio_file}: {exc}")

        # Return audio file with async cleanup
        return FileResponse(
            audio_file,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(audio_file)}"},
            background=cleanup_file
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
