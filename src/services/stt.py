"""Speech-to-text service — cloud preferred, local fallback."""

from __future__ import annotations

import asyncio
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


class STTService:
    async def transcribe(self, audio_path: str) -> str:
        if settings.stt_cloud_api_key:
            return await self._cloud_transcribe(audio_path)
        return await self._local_transcribe(audio_path)

    async def _cloud_transcribe(self, audio_path: str) -> str:
        try:
            from groq import Groq
            def _sync_transcribe() -> str:
                client = Groq(api_key=settings.stt_cloud_api_key)
                with open(audio_path, "rb") as f:
                    resp = client.audio.transcriptions.create(
                        file=f,
                        model="whisper-large-v3",
                    )
                return resp.text or ""
            return await asyncio.to_thread(_sync_transcribe)
        except Exception as exc:
            logger.warning("cloud_stt_failed", error=str(exc))
            return await self._local_transcribe(audio_path)

    async def _local_transcribe(self, audio_path: str) -> str:
        try:
            import whisper
            def _sync_transcribe() -> str:
                model = whisper.load_model(settings.stt_local_model)
                result = model.transcribe(audio_path)
                return result.get("text", "")
            return await asyncio.to_thread(_sync_transcribe)
        except Exception as exc:
            logger.error("local_stt_failed", error=str(exc))
            return "[STT unavailable]"
