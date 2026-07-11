"""Tests for Search MCP server — DuckDuckGo backend."""

from __future__ import annotations

import pytest

from src.mcp.servers.search import SearchMCPServer


@pytest.mark.asyncio
async def test_search_returns_results() -> None:
    server = SearchMCPServer()
    results = await server.call_tool("web_search", {"query": "python programming", "max_results": 3})
    assert isinstance(results, list)
    assert len(results) <= 3
    if results:
        assert "title" in results[0]
        assert "url" in results[0]
        assert "snippet" in results[0]


@pytest.mark.asyncio
async def test_search_no_api_key_required() -> None:
    server = SearchMCPServer()
    results = await server.call_tool("web_search", {"query": "test"})
    assert isinstance(results, list)
