"""MCP client for connecting to MCP servers."""

from __future__ import annotations

from typing import Any

import httpx


class MCPClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def list_tools(self, server: str) -> list[dict[str, Any]]:
        resp = await self._client.get(f"{self._base_url}/servers/{server}/tools")
        resp.raise_for_status()
        return resp.json().get("tools", [])

    async def call_tool(self, server: str, tool: str, arguments: dict[str, Any], agent: str = "cli") -> Any:
        resp = await self._client.post(
            f"{self._base_url}/tools/call",
            json={"agent": agent, "server": server, "tool": tool, "arguments": arguments},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data.get("result")

    async def close(self) -> None:
        await self._client.aclose()
