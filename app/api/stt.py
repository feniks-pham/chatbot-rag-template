import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.stt import STTService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
stt_service = STTService()

@router.post("/stt-zalo")
async def speech_to_text(
    audio_file: UploadFile = File(..., description="Audio file (e.g., WAV)"),
    encoding_type: str = Form("wav"),  # "wav" theo mẫu API của VNG Cloud
):
    """
    Convert speech (audio file) to text using Zalo/VNG Cloud STT (sync).
    Trả về: {"text": "..."}
    """
    try:
        # Đọc bytes từ UploadFile
        content = await audio_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file.")

        filename = audio_file.filename or f"upload.{encoding_type}"
        content_type = audio_file.content_type or "audio/wav"

        logger.info(
            f"STT request: filename='{filename}', content_type='{content_type}', "
            f"encoding_type='{encoding_type}', size={len(content)} bytes"
        )

        # Gọi service (dùng bytes để không phải ghi ra file tạm)
        transcript = await stt_service.transcribe_bytes(
            content,
            filename=filename,
            encoding_type=encoding_type,
            content_type=content_type,
        )

        return {"text": transcript}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Speech-to-text failed")
    finally:
        try:
            await audio_file.close()
        except Exception:
            pass