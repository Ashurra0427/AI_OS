"""Speech pipeline combining STT and TTS."""

from __future__ import annotations

from src.services.stt import STTService
from src.services.tts import TTSService


class SpeechPipeline:
    def __init__(self) -> None:
        self._stt = STTService()
        self._tts = TTSService()

    async def transcribe(self, audio_path: str) -> str:
        return await self._stt.transcribe(audio_path)

    async def speak(self, text: str, output_path: str) -> str:
        return await self._tts.speak(text, output_path)
