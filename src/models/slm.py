"""Small Language Model (SLM) — fast local responses.

Always-warm, device-only tier. This implementation uses a lightweight
keyword-matching fallback when the heavy local LLM is unavailable or too slow.
Swap the fallback for a real quantized SLM (e.g. Qwen2.5-0.5B) later.
"""

from __future__ import annotations

import asyncio
import logging
import time

from src.models.llm import LLM

logger = logging.getLogger(__name__)


class SLM:
    def __init__(self) -> None:
        self._llm = LLM(local=True)
        self._fast_responses: dict[str, str] = {
            "ping": "pong",
            "hello": "Hi! How can I help?",
            "hi": "Hello! What do you need?",
            "status": "All systems operational.",
            "time": time.strftime("%H:%M:%S"),
            "date": time.strftime("%Y-%m-%d"),
        }

    async def respond(self, prompt: str) -> str:
        text = prompt.strip().lower()
        for keyword, response in self._fast_responses.items():
            if keyword in text:
                return response
        try:
            return await asyncio.wait_for(self._llm.generate(prompt), timeout=2.0)
        except Exception as exc:
            logger.warning("slm_fallback", error=str(exc))
            return f"[SLM fallback] I heard: {prompt[:50]}"
