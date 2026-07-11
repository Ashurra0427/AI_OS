"""RAG — hybrid dense + sparse retrieval."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self) -> None:
        self._documents: list[dict[str, Any]] = []
        self._dense_index: Any = None
        self._sparse_index: Any = None

    def add_document(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self._documents.append({"id": doc_id, "text": text, "metadata": metadata or {}})
        logger.debug("rag_document_added", doc_id=doc_id)

    def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not self._documents:
            return []
        scored = []
        for doc in self._documents:
            score = self._bm25_score(query_text, doc["text"])
            scored.append({**doc, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _bm25_score(self, query: str, text: str) -> float:
        query_terms = set(query.lower().split())
        text_lower = text.lower()
        if not query_terms:
            return 0.0
        matches = sum(1 for t in query_terms if t in text_lower)
        return matches / max(len(query_terms), 1)
