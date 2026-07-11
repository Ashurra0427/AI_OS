"""Search/research MCP server — backed by Tavily real search API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config.settings import settings

logger = logging.getLogger(__name__)


class SearchMCPServer:
    def __init__(self) -> None:
        self.tools = [
            {
                "name": "web_search",
                "description": "Search the web using Tavily API",
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
        if not settings.search_api_key:
            raise RuntimeError("search_api_key not configured")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                settings.search_api_url,
                json={"query": query, "max_results": max_results},
                headers={"X-TAVILY-API-KEY": settings.search_api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                })
            if not results:
                logger.warning("search_returned_empty", query=query)
            return results

    async def _fetch_url(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text[:50000]
