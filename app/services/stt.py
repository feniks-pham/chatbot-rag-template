import os
import httpx
import aiofiles
from typing import Optional
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class STTService:
    def __init__(self):
        self.api_url = settings.stt_api_url
        self.api_key = settings.stt_api_key
        self.model = settings.stt_model
        self.encoding_type = settings.stt_encoding_type
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def speech_to_text(self, audio_path: str) -> str:
        """Convert speech (audio file) to text using Zalo STT API"""
        try:
            logger.info(f"Starting STT process for audio file: {audio_path}")

            # Read audio file as bytes
            async with aiofiles.open(audio_path, "rb") as f:
                audio_bytes = await f.read()

            # Prepare multipart/form-data
            multipart_data = {
                "audio_file": (os.path.basename(audio_path), audio_bytes, "audio/mpeg"),
                "encoding_type": (None, self.encoding_type),
                "model": (None, self.model)
            }
            logger.debug(f"Sending request to {self.api_url} with model={self.model} and encoding={self.encoding_type}")

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    files=multipart_data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                text = result.get("results", [{}])[0].get("transcript", "")
                logger.info(f"STT Result: {text}")
                return text

        except Exception as e:
            logger.error(f"Error during STT processing: {e}", exc_info=True)
            raise