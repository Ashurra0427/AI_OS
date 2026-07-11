"""Search/research MCP server — backed by DuckDuckGo (free, no API key required)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SearchMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {
                "name": "web_search",
                "description": "Search the web using DuckDuckGo (free, no API key required)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "description": "Max results", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "fetch_url",
                "description": "Fetch raw content from a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"},
                    },
                    "required": ["url"],
                },
            },
        ]

    async def call_tool(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool == "web_search":
            return await self._web_search(
                str(arguments["query"]),
                int(arguments.get("max_results", 5)),
            )
        elif tool == "fetch_url":
            return await self._fetch_url(str(arguments["url"]))
        else:
            raise ValueError(f"Unknown tool: {tool}")

    async def _web_search(self, query: str, max_results: int) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body"),
                })
            if not results:
                logger.warning("search_returned_empty query=%s", query)
            return results
        except Exception as exc:
            logger.error("search_failed query=%s error=%s", query, str(exc))
            raise RuntimeError(f"DuckDuckGo search failed: {exc}") from exc

    async def _fetch_url(self, url: str) -> str:
        import httpx
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text[:50000]
