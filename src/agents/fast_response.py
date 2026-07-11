"""Fast-Response Agent — instant handling of trivial commands via SLM."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.models.slm import SLM


class FastResponseAgent(BaseAgent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("name", "fast")
        super().__init__(*args, **kwargs)
        self._slm = SLM()

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        text = str(task.get("text", ""))
        self.log("fast_response", text=text[:100])
        import time
        start = time.perf_counter()
        response = await self._slm.respond(text)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {"response": response, "latency_ms": latency_ms}
