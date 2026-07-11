"""Tests for Search MCP server."""

from __future__ import annotations

import httpx
import pytest

from src.config.settings import settings
from src.mcp.servers.search import SearchMCPServer


@pytest.mark.asyncio
async def test_search_without_key() -> None:
    original = settings.search_api_key
    settings.search_api_key = None
    try:
        server = SearchMCPServer()
        with pytest.raises(RuntimeError, match="search_api_key not configured"):
            await server.call_tool("web_search", {"query": "test"})
    finally:
        settings.search_api_key = original


@pytest.mark.asyncio
async def test_search_forced_failure_logs() -> None:
    server = SearchMCPServer()
    original_key = settings.search_api_key
    settings.search_api_key = "invalid-key"
    try:
        with pytest.raises(httpx.HTTPStatusError):
            await server.call_tool("web_search", {"query": "test"})
    finally:
        settings.search_api_key = original_key
