"""Text-to-speech service — cloud preferred, local fallback."""

from __future__ import annotations

import asyncio
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


class TTSService:
    async def speak(self, text: str, output_path: str) -> str:
        if settings.tts_cloud_provider == "edge":
            return await self._edge_tts(text, output_path)
        return await self._local_tts(text, output_path)

    async def _edge_tts(self, text: str, output_path: str) -> str:
        try:
            import edge_tts
            def _sync_save() -> str:
                communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
                import asyncio as _asyncio
                _asyncio.run(communicate.save(output_path))
                return output_path
            return await asyncio.to_thread(_sync_save)
        except Exception as exc:
            logger.warning("edge_tts_failed", error=str(exc))
            return await self._local_tts(text, output_path)

    async def _local_tts(self, text: str, output_path: str) -> str:
        try:
            def _sync_generate() -> str:
                from kokoro import KPipeline
                pipeline = KPipeline(lang_code="a")
                audio = pipeline(text, voice="af_heart")
                import soundfile as sf
                sf.write(output_path, audio, 24000)
                return output_path
            return await asyncio.to_thread(_sync_generate)
        except Exception as exc:
            logger.error("local_tts_failed", error=str(exc))
            return "[TTS unavailable]"
