"""Planner/Orchestrator agent — decomposes requests, delegates, tracks progress."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.models.router import MoERouter


class PlannerAgent(BaseAgent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("name", "planner")
        super().__init__(*args, **kwargs)
        self._router = MoERouter()

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("decompose", task=str(task)[:200])
        text = str(task.get("text", ""))
        route = await self._router.route({"text": text})
        steps = [
            {"step": 1, "agent": "research", "action": "search", "query": text, "route": route},
            {"step": 2, "agent": "analysis", "action": "summarize", "source": "research"},
        ]
        return {"plan": steps, "status": "decomposed", "route": route}
