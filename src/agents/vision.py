"""Vision/Automation agent — screen understanding and desktop control."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.models.lam import LAM
from src.models.sam import SAM
from src.models.vlm import VLM


class VisionAutomationAgent(BaseAgent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("name", "vision")
        super().__init__(*args, **kwargs)
        self._vlm = VLM()
        self._sam = SAM()
        self._lam = LAM(mcp_client=self._mcp)

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("vision", task=str(task)[:200])
        action = task.get("action", "analyze")
        if action == "analyze":
            image = str(task.get("image", ""))
            if not image:
                return {"status": "error", "error": "image path required"}
            ocr_text = await self._vlm.ocr(image)
            elements = self._sam.segment(image)
            return {"status": "analyzed", "ocr": ocr_text, "screen_elements": elements}
        elif action == "click":
            return await self._lam.execute("click", {"x": int(task.get("x", 0)), "y": int(task.get("y", 0)), "button": str(task.get("button", "left"))})
        elif action == "type":
            return await self._lam.execute("type", {"text": str(task.get("text", ""))})
        return {"status": "unknown_action"}
