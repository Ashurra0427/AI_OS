"""Research agent — web research, multi-source synthesis."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("research", query=str(task.get("query", ""))[:200])
        query = str(task.get("query", ""))
        results = []
        if self._mcp:
            try:
                results = await self.call_mcp("search", "web_search", {"query": query, "max_results": 5})
            except Exception as exc:
                self.log("search_error", error=str(exc))
        return {"query": query, "results": results, "status": "completed"}
