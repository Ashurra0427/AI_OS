"""Tests for RAG engine."""

from __future__ import annotations

from src.models.rag import RAGEngine


def test_rag_add_and_query() -> None:
    engine = RAGEngine()
    engine.add_document("doc1", "Python is a programming language")
    engine.add_document("doc2", "JavaScript runs in browsers")
    results = engine.query("python programming", top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
