# app/services/stt.py
import os
import json
import mimetypes
from typing import Optional, Any

import httpx
import aiofiles

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class STTService:
    """
    Zalo/VNG Cloud STT (sync) – phiên bản khớp curl mới:
      POST https://maas-llm-aiplatform-hcm.api.vngcloud.vn/maas/user-60108/zaloai/zalo-stt-vi/v1/speech/stt
      multipart/form-data: audio_file, encoding_type, model
    """
    def __init__(self):
        self.api_url: str = getattr(
            settings, "stt_api_url",
            "https://maas-llm-aiplatform-hcm.api.vngcloud.vn/maas/user-60108/zaloai/zalo-stt-vi/v1/speech/stt",
        )
        self.api_key: str = settings.stt_api_key
        self.model: str = getattr(settings, "stt_model", "zalo-stt-vi")
        self.timeout: float = float(getattr(settings, "stt_timeout", 60.0))

        # KHÔNG set Content-Type thủ công cho multipart
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    def _guess_mime(self, filename: str, default: str = "audio/mpeg") -> str:
        mime, _ = mimetypes.guess_type(filename)
        return mime or default

    def _infer_encoding_from_mime(self, mime: str) -> str:
        m = (mime or "").lower()
        if "wav" in m:
            return "wav"
        if "mpeg" in m or "mp3" in m:
            return "mp3"
        if "webm" in m:
            return "webm"
        # fallback hợp lý cho hầu hết client upload mp3
        return "mp3"

    def _extract_text_from_response(self, data: Any) -> str:
        """
        Linh hoạt bóc transcript từ payload JSON/text.
        Điều chỉnh key nếu response schema của bạn khác.
        """
        try:
            if isinstance(data, str):
                data = json.loads(data)
        except Exception:
            return str(data)

        if isinstance(data, dict):
            # các khóa thường gặp
            for key in ("text", "transcript", "result", "message"):
                v = data.get(key)
                if isinstance(v, str) and v.strip():
                    return v

            # segments -> ghép
            if isinstance(data.get("segments"), list):
                segs = [seg.get("text", "") for seg in data["segments"] if isinstance(seg, dict)]
                segs = [s for s in segs if s]
                if segs:
                    return " ".join(segs)

            # alternatives[0].text
            alts = data.get("alternatives")
            if isinstance(alts, list) and alts:
                if isinstance(alts[0], dict) and isinstance(alts[0].get("text"), str):
                    return alts[0]["text"]

            # nếu response bọc trong "data"
            if "data" in data:
                return self._extract_text_from_response(data["data"])

        try:
            return json.dumps(data, ensure_ascii=False)
        except Exception:
            return str(data)

    async def transcribe_file(
        self,
        file_path: str,
        *,
        encoding_type: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # đọc bytes để an toàn với async
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        filename = os.path.basename(file_path)
        mime = self._guess_mime(filename, default="audio/mpeg")
        enc = (encoding_type or self._infer_encoding_from_mime(mime)).lower()
        mdl = model or self.model

        logger.info(
            f"STT(file) -> url='{self.api_url}', model='{mdl}', encoding_type='{enc}', "
            f"filename='{filename}', mime='{mime}', size={len(content)} bytes"
        )

        files = {
            "audio_file": (filename, content, mime),
        }
        data = {
            "encoding_type": enc,
            "model": mdl,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.api_url, headers=self.headers, data=data, files=files)
                resp.raise_for_status()
                try:
                    payload = resp.json()
                except Exception:
                    payload = resp.text
                transcript = self._extract_text_from_response(payload)
                logger.info(f"STT success. Transcript length: {len(transcript)} chars")
                return transcript
        except httpx.HTTPStatusError as e:
            logger.error(f"STT HTTP error: status={e.response.status_code}, body={e.response.text}")
            raise
        except Exception as e:
            logger.error(f"STT error: {e}", exc_info=True)
            raise

    async def transcribe_bytes(
        self,
        audio_bytes: bytes,
        *,
        filename: str = "audio.mp3",
        encoding_type: Optional[str] = None,
        content_type: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        mime = content_type or self._guess_mime(filename, default="audio/mpeg")
        enc = (encoding_type or self._infer_encoding_from_mime(mime)).lower()
        mdl = model or self.model

        logger.info(
            f"STT(bytes) -> url='{self.api_url}', model='{mdl}', encoding_type='{enc}', "
            f"filename='{filename}', mime='{mime}', size={len(audio_bytes)} bytes"
        )

        files = {
            "audio_file": (filename, audio_bytes, mime),
        }
        data = {
            "encoding_type": enc,
            "model": mdl,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.api_url, headers=self.headers, data=data, files=files)
                resp.raise_for_status()
                try:
                    payload = resp.json()
                except Exception:
                    payload = resp.text
                transcript = self._extract_text_from_response(payload)
                logger.info(f"STT success. Transcript length: {len(transcript)} chars")
                return transcript
        except httpx.HTTPStatusError as e:
            logger.error(f"STT HTTP error: status={e.response.status_code}, body={e.response.text}")
            raise
        except Exception as e:
            logger.error(f"STT error: {e}", exc_info=True)
            raise
