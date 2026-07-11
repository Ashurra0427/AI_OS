"""Vision Language Model (VLM) — screen understanding and OCR."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VLM:
    def __init__(self, model: str = "openai/gpt-4o") -> None:
        self.model = model

    async def analyze(self, image_path: str, prompt: str) -> dict[str, Any]:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        try:
            import openai
            client = openai.AsyncOpenAI()
            with open(image_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                        ],
                    }
                ],
                max_tokens=1024,
            )
            text = resp.choices[0].message.content or ""
            return {"text": text, "model": self.model}
        except Exception as exc:
            logger.error("vlm_analysis_failed error=%s", str(exc))
            return {"text": "[VLM unavailable]", "error": str(exc), "model": self.model}

    async def ocr(self, image_path: str) -> str:
        try:
            result = await self.analyze(image_path, "Extract all text from this image. Return only the text.")
            return result.get("text", "")
        except FileNotFoundError:
            return "[VLM unavailable]"
