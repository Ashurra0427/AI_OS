"""Large Action Model (LAM) — desktop action execution via MCP."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class LAM:
    def __init__(self, mcp_client: Any | None = None) -> None:
        self._mcp = mcp_client
        self._history: list[dict[str, Any]] = []

    async def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if self._mcp is None:
            raise RuntimeError("LAM requires an MCP client")
        tool_map = {
            "click": ("input_injection", "click"),
            "type": ("input_injection", "type"),
            "hotkey": ("input_injection", "hotkey"),
            "navigate": ("browser", "navigate"),
            "screenshot": ("browser", "screenshot"),
        }
        if action not in tool_map:
            raise ValueError(f"Unsupported LAM action: {action}")
        server, tool = tool_map[action]
        result = await self._mcp.call_tool(server, tool, parameters)
        record = {"action": action, "parameters": parameters, "result": result}
        self._history.append(record)
        logger.info("lam_executed", action=action, result=str(result)[:200])
        if isinstance(result, dict):
            return result
        return {"status": "ok", "result": result}

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._history)
