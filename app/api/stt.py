import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.stt import STTService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
stt_service = STTService()

@router.post("/stt-zalo")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        # Save temp file
        suffix = f".{audio_file.filename.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await audio_file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Call STT service
        transcript = await stt_service.speech_to_text(tmp_path)

        # Delete temp file
        os.remove(tmp_path)

        return {"transcript": transcript}

    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))