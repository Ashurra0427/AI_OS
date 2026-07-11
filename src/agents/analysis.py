"""Analysis agent — data/document reasoning with RAG."""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent
from src.models.rag import RAGEngine


class AnalysisAgent(BaseAgent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("name", "analysis")
        super().__init__(*args, **kwargs)
        self._rag = RAGEngine()

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        self.log("analyze", task=str(task)[:200])
        query = str(task.get("text", task.get("query", "")))
        docs = []
        if query:
            self._rag.add_document("query_context", query)
            docs = self._rag.query(query, top_k=3)
        return {"status": "analyzed", "query": query, "documents": docs, "summary": f"Analyzed {len(docs)} documents"}
